# Module Sandboxing Audit Report

## Module Information
- **Name**: proj
- **Version**: 1.1
- **Type**: C++ (binary module)
- **Audit Date**: 2026-04-23
- **Safe for Sandbox Use**: Conditional — see "Network Security" below

## Domain
- **Functional Domain**: `QDOM_DEFAULT`
- **Rationale**: The proj module itself performs no direct filesystem,
  network, subprocess, or environment-variable access in its own C++
  code. However, the underlying libproj library does read files from
  disk (the PROJ resource directory: `proj.db`, grid-shift files,
  `.tif` CDN files) and *may* access the network if PROJ's CDN mode is
  enabled. See the Filesystem and Network sections below for the full
  picture.

## Filesystem Security

- [x] Module source code performs no direct filesystem operations
      (no `fopen`, `open`, `fstream`, `ifstream`, `ofstream`, `stat`,
      `unlink`, etc.) — verified by grep.
- [x] Module does not call `proj_context_set_search_paths()`,
      `proj_context_set_database_path()`, or
      `proj_context_set_user_writable_directory()` — the Qore caller
      cannot inject arbitrary filesystem paths into libproj.
- [ ] **Indirect filesystem reads by libproj**: every PROJ context
      created via `proj_context_create()` reads `proj.db` (SQLite) plus
      any grid-shift files (`.tif`, `.gsb`) needed for a given
      transformation. libproj resolves these files by searching:
      1. Paths from the `PROJ_DATA` (or legacy `PROJ_LIB`) environment
         variable,
      2. The compile-time `PROJ_LIB_DIR` (typically
         `/usr/share/proj` or `/opt/homebrew/share/proj`),
      3. The user-writable directory
         (`~/.local/share/proj` on Linux, `~/Library/Application
         Support/proj` on macOS).

- **Gaps Found**: None in the module itself. The libproj filesystem
  reads are outside Qore's filesystem security manager: libproj uses
  direct C library calls (`fopen`, `mmap`), not `QoreFile` / `QoreDir`,
  so `QoreFilesystemSecurityManager::checkAccess()` is **not
  consulted**.
- **Severity**: Low. The files read are well-known, install-time
  resource files whose contents are public (CRS definitions, datum
  shift grids). A malicious Qore caller cannot redirect these reads
  to arbitrary paths through the module's own API surface — the search
  paths come from the process environment at libproj init time.
- **Operator recommendation**: when loading this module into a sandbox
  that restricts filesystem reads, the sandbox policy must explicitly
  **allow reads** under the PROJ resource directory (typically
  `/usr/share/proj/**` or whatever `$PROJ_DATA` points to). Otherwise
  `ProjTransformer` construction will fail with
  `proj_create_crs_to_crs()` returning null for even standard EPSG
  codes.
- **Threat-model note**: the `PROJ_DATA` / `PROJ_LIB` env var is
  honored by libproj and can redirect resource lookup to an
  attacker-controlled path. Sandbox operators should scrub these env
  vars or pre-set them to a trusted directory before loading the
  module.

## Network Security

- [x] Module source code performs no direct network operations
      (no `socket`, `connect`, `bind`, `getaddrinfo` — verified by
      grep).
- [x] Module **explicitly disables** libproj's network-CDN feature:
      `proj_get_context()` calls `proj_context_set_enable_network(ctx,
      0)` immediately after `proj_context_create()`. This overrides
      any `PROJ_NETWORK=ON` environment variable for every context
      the module creates, closing the env-var-bypass SSRF surface.
      See `src/proj-module.cpp` `proj_get_context()`.
- [x] Module does not call any other network-enabling API
      (`proj_context_set_url_endpoint`,
      `proj_context_set_network_callbacks`, etc.) — verified by grep.

- **Gaps Found**: None at the module boundary. A caller who obtained
  a raw `PJ_CONTEXT*` through some future unexported interface could
  re-enable network; today there is no such interface.
- **Severity**: None.

## Process / Environment Security
- [x] No subprocess invocation
- [x] No direct environment variable access from the module — libproj
      reads its own env vars (`PROJ_DATA`, `PROJ_LIB`, `PROJ_NETWORK`,
      `PROJ_DEBUG`) at init time.
- **Gaps Found**: env-var influence on libproj behavior, covered in
  Filesystem and Network above.
- **Severity**: Low

## Resource Limits

- [x] `ProjTransformer` constructor allocates one `PJ*` per thread via
      `proj_create_crs_to_crs()`. Memory per transformer is bounded by
      libproj internals (CRS descriptors + grid metadata + SQLite
      connection to `proj.db`). A typical `EPSG:4326 → EPSG:25832`
      transformer is a few hundred KB.
- [x] `transform()` / `transformInverse()` (single point): constant
      time, microsecond latency.
- [x] `transformBatch()` / `transformInverseBatch()`: one
      `proj_trans_generic()` call for the whole input — linear in the
      number of points, no intermediate allocations beyond the two
      `std::vector<double>` (xs, ys) used to bundle coordinates.
- [x] Geodesic helpers (`great_circle_distance`, `forward_azimuth`,
      `inverse_azimuth`): constant time, no allocations.
- [x] No native threads spawned by the module.

- **Gaps Found**: `transformBatch` / `transformInverseBatch` allocate
  `O(n)` memory proportional to the input list size. A malicious or
  buggy caller passing a 100-million-element list can exhaust memory.
  This is bounded by the caller and visible to Qore's own allocation
  tracking (the `list<auto>` parameter is counted at Qore level).
  The input marshalling, libproj call, and output wrapping are all
  cooperatively cancellable, so a runaway allocator can still be
  interrupted via `cancel_thread()` or
  `SandboxManager::requestInterrupt()`.
- **Severity**: Low — user-controlled input size, standard
  resource-limit territory.

## Interrupt Support / Cooperative Cancellation

- [x] Pre-operation `qore_check_cancel()` (Pattern 1) at the head of
      every public entry point: constructor, `transform()`,
      `transformInverse()`, `transformBatch()`, `transformInverseBatch()`,
      and `getPj()` before the expensive first-time CRS setup that
      reads `proj.db` and grid-shift files.
- [x] Batch-chunked `proj_trans_generic()` calls: both batch methods
      process the input in `PROJ_BATCH_CHUNK` (= 4096 points) chunks
      with a cancellation check between chunks. This bounds
      cancellation latency on a million-point batch to the wall time
      of one 4096-point chunk — well under the 500 ms polling budget
      on any modern CPU for typical EPSG pairs.
- [x] Periodic `qore_check_cancel()` (Pattern 5) every
      `PROJ_CHECK_EVERY` (= 1000) iterations in the input-marshalling
      and output-wrapping loops, so the cheap-per-point loops don't
      themselves become a cancellation blind spot on very large
      inputs.
- [x] Geodesic helpers (`great_circle_distance`, `forward_azimuth`,
      `inverse_azimuth`) complete in microseconds per call — no
      polling needed.

- **Gaps Found**: None.
- **Severity**: None.

## Thread Safety Disclosure

- **ProjTransformer**: thread-safe for concurrent use. Each thread
  gets its own `PJ_CONTEXT` (thread-local, lazily created in
  `proj_get_context()`) and its own `PJ*` (per-transformer
  `std::unordered_map<thread::id, PJ*>` guarded by a `std::mutex`).
  libproj requires each `PJ` to be used only with the context it was
  created under; this invariant is enforced by the per-thread PJ
  cache.
- **Module-level state**: the `QoreNamespace PNS("Qore::PROJ")` is the
  only global, initialized once at module load. No mutable module-
  level state.
- **Thread-local cleanup**: `PJ_CONTEXT` is intentionally **not**
  destroyed at thread exit (see `proj-module.cpp:51-54`). Contexts
  leak at process shutdown only; they are small and bounded. A
  long-lived thread pool sees at most one context leak per worker,
  which is negligible.

## Callback Handling

None — the proj module does not invoke user-supplied Qore callbacks.

## Summary
- **Compliance Level**: Full at the module boundary. Module source
  does no direct filesystem or network I/O; libproj's CDN is hard-
  disabled per-context regardless of `PROJ_NETWORK`; every public
  entry point is cooperatively cancellable.
- **Highest Severity Finding**: Low (operator-level filesystem-
  whitelist requirement — intrinsic to libproj, not a module bug).
- **Recommendation**: Safe for sandbox use **provided that** the
  sandbox filesystem policy allows reads under the PROJ resource
  directory (`/usr/share/proj` or wherever `$PROJ_DATA` points), and
  `PROJ_DATA` / `PROJ_LIB` env vars are scrubbed or pre-set to a
  trusted path.

## Specific Findings

| # | Location | Description | Severity | Remediation |
|---|----------|-------------|----------|-------------|
| 1 | libproj, indirect | libproj reads `proj.db` and grid-shift files from paths resolved via `PROJ_DATA` / `PROJ_LIB` / compile-time default. Bypasses `QoreFilesystemSecurityManager`. | Low | Sandbox operators must whitelist the PROJ resource directory and scrub `PROJ_DATA` / `PROJ_LIB` env vars. Not fixable in the module. |
