OBS absolute file dependency audit
==================================

Copyright 2026 Qore Technologies, s.r.o.

Scope: packaging-only literal GEOS tag-file BuildRequires, release 4, changelog, and RPM README. Local rpmspec and provider checks pass on Fedora, Leap, and EL10. OBS buildinfo selects qore-geos-module-doc on Fedora/Leap; EL10 has only the documented MongoDB ABI mismatch pending the in-progress Qore rebuild.

.. list-table:: Complete audit-changes checklist
   :header-rows: 1

   * - Check
     - Status
     - Evidence

   * - 1. Entry exists in doxygen/lang/120_modules.dox.tmpl (for modules in the Qore repo; N/A for external module repos)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 2. Entry exists in doxygen/lang/900_release_notes.dox.tmpl (for modules in the Qore repo; external modules have release notes in their .qm)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 3. qore_user_module() or qore_external_user_module() call in CMakeLists.txt
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 4. Module added to QMOD list in CMakeLists.txt
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 5. .qm file has @section <lowercasemodname>intro as first doc section — must be all lowercase (e.g., avrodataproviderintro, not AvroDataProviderintro)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 6. %modern in .qm file — no redundant %new-style, %require-types, %strict-args, %enable-all-warnings
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 7. No parse directives (%requires, %modern, %new-style) in separated .qc files (check OUTSIDE of @code blocks only)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 8. No %include usage (deprecated for modules)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 9. Copyright 2026 on all new files
     - Pass
     - 2026 copyright retained.

   * - 10. Directory layout: .qm inside qlib/<ModuleName>/ directory (not at qlib/<ModuleName>.qm for multi-file modules)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 11. No second .qm for the same module at qlib/<ModuleName>.qm
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 12. ns=Qore::XX matches the QoreNamespace constructor path
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 13. %modern directive present
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 14. Executable permission set (chmod +x)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 15. Uses %prepend-module-path  before %requires for in-repo modules (Qore and Qore modules only; not Qorus)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 16. External module dependencies use %try-module — except modules delivered with the project itself (Qore ex: DataProvider, ConnectionProvider, QUnit, etc.) which use hard %requires
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 17. No filesystem operations (fopen, open, creat, unlink, remove, rename, mkdir, rmdir, stat, chmod) without sandbox checks
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 18. No network operations (connect, bind, socket, getaddrinfo, gethostbyname) without sandbox checks
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 19. If filesystem/network ops exist, verify QoreSandboxManagerHelper usage
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 20. No File::, Dir::, Socket::, HTTPClient:: usage without justification
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 21. All for/while loops that could iterate >100 times have qore_check_cancel() checks
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 22. Uses qore_check_cancel() (NOT deprecated qore_check_io_interrupt())
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 23. Check frequency: every 100 iterations for tight loops, every 10 for expensive iterations
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 24. No blocking operations without cancellation support
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 25. Every action has display_name, short_desc (plain text, <80 chars), desc (markdown)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 26. Every action has options populated via getActionOptionFromFields() — without this, the action shows an empty, unusable form
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 27. Every action has output_type set to a typed data type constant (e.g., MyResponseDataType) — not omitted
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 28. DPAT_API actions: provider has "supports_request": True and implements doRequestImpl()
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 29. DPAT_FIND actions: every option exists in SearchOptions, getRecordTypeImpl() returns *hash<string, AbstractDataField>
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 30. Scheme-based apps (with "scheme" in registerApp): actions use "path" and do NOT use "cls" — having both scheme and cls causes a runtime error
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 31. Single-key hash slices use trailing comma: Fields{"key",} (without trailing comma, Fields{"key"} returns the value, not a hash)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 32. Typed data type classes exist for request and response types — inherit HashDataType, have const Fields hash, call addQoreFields(Fields) in constructor, export public constant at bottom (e.g., public const MyDataType = new MyDataType();)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 33. Request/input types use public Fields (enables ClassName::Fields in action registration)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 34. Response/output types use private Fields
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 35. Each field in data types has display_name, type, and desc (markdown-formatted)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 36. Input fields have example_value where useful (string fields, endpoint URIs, SQL queries, etc.)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 37. Fields with finite allowed values use allowed_values with AllowedValueInfo containing both value and display_name (Title Case, human-readable) — never bare values, never described only in text
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 38. Password/secret fields have "sensitive": True
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 39. groups uses AppGroup enum values from qlib/DataProvider/AppGroup.qc
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 40. App logo stored as separate file, loaded at module level in Priv namespace
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 41. App desc uses markdown: bullet list of capabilities, links to project website, business-language explanation of value
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 42. display_name is user-friendly ("Apache Avro" not "avro")
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 43. short_desc is plain text, under 80 chars, single sentence — no markdown
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 44. desc uses markdown: backticks for code/field refs ( field_name ,  True ,  pdf ), \n\n for paragraphs, -  bullet lists for enumerations, bold for caveats
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 45. Descriptions use plain business language relating to common challenges — not just technical "what" but "why" and "when to use"
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 46. No bare True/False/NOTHING — must be backtick-wrapped in desc
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 47. No bare field/option names in prose — must use backticks
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 48. Long descriptions (>500 chars) use bold section headers and bullet lists
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 49. Factory registration in Qore repo: every factory name registered in qlib/DataProvider/DataProvider.qc → FactoryMap (without this, module loads but doesn't appear in Qorus apps)
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 50. getRecordTypeImpl() signature: must be private *hash<string, AbstractDataField> getRecordTypeImpl(*hash<auto> search_options) — NOT returning *AbstractDataProviderType
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 51. Dependency JARs committed (for JNI modules): JAR files in qlib/*/jar/ may be gitignored — use git add -f to ensure they're tracked, otherwise CI compilation fails
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 52. JAR install rules in CMakeLists.txt for all dependency JARs
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 53. No workarounds: No TODOs, FIXMEs, stubs, or partially-implemented features
     - Pass
     - A literal filesystem dependency is required by OBS parsing; the exact tag file remains mandatory.

   * - 54. Exception safety: C++ uses ReferenceHolder for Qore allocations, std::unique_ptr for C++ allocations, *xsink checked after every fallible operation
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 55. Thread safety: All mutable shared state protected by std::lock_guard<std::mutex> or documented as immutable-after-construction
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 56. Type safety: Strongly-typed code<return(args)> instead of untyped code; static_cast instead of C casts; typed hashdecls for results; enums where appropriate
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 57. Performance: No O(n²) where O(n) is possible; no unnecessary copies; coordinate descent uses incremental residuals not full matrix multiply
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 58. Error handling: All inputs validated (dimensions, empty data, unfitted models); C++ I/O handles EAGAIN/EINTR if applicable
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 59. Documentation: Doxygen @param, @return, @throw on all public methods; @par Example with realistic business scenarios; @note for important caveats
     - Pass
     - Changelog and RPM README explain the literal dependency and existing FileProvides mapping.

   * - 60. QPP flags: [flags=CONSTANT] on methods that never throw; [flags=RET_VALUE_ONLY] on methods that throw but have no side effects
     - N/A
     - Packaging and documentation only; no relevant runtime/module/provider implementation is changed.

   * - 61. Security: No user-controlled format strings; no buffer overflows; bounds checking on array indices; no credentials in code
     - Pass
     - No credentials or new executable behavior.

   * - 62. Correctness: Algorithms verified against reference implementations; edge cases tested (empty data, single sample, all-zero features)
     - Pass
     - All three local dependency queries resolve the actual installed tag. Server-side candidate buildinfo removes the literal macro failure; no target qualification is inferred from the pending EL10 core rebuild.
