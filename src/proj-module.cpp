/* -*- mode: c++; indent-tabs-mode: nil -*- */
/*
    proj-module.cpp

    Qore Programming Language

    Copyright (C) 2026 Qore Technologies, s.r.o.

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
*/

#include "proj-module.h"

static void proj_module_init(QoreModuleInitContext& ctx, ExceptionSink& xsink);
static void proj_module_ns_init(QoreNamespace* rns, QoreNamespace* qns, ExceptionSink& xsink);
static void proj_module_delete();

extern "C" DLLEXPORT void proj_qore_module_desc(QoreModuleInfo& mod_info) {
    mod_info.name = "proj";
    mod_info.version = PACKAGE_VERSION;
    mod_info.desc = "PROJ coordinate transformation module";
    mod_info.author = "Qore Technologies, s.r.o.";
    mod_info.url = "https://github.com/qoretechnologies/module-proj";
    mod_info.api_major = QORE_MODULE_API_MAJOR;
    mod_info.api_minor = QORE_MODULE_API_MINOR;
    mod_info.init = proj_module_init;
    mod_info.ns_init = proj_module_ns_init;
    mod_info.del = proj_module_delete;
    mod_info.license = QL_MIT;
    mod_info.license_str = "MIT";
}

// Thread-local PROJ context handle.
// Lazily created on first use per thread; lives until thread exit.
// PROJ context ownership: proj_context_destroy() is NOT called on thread
// shutdown here because POSIX doesn't give us a portable per-thread destructor
// hook without pthread_key_create, and PROJ contexts leaking at thread
// termination is cheap (small, bounded, only happens at process shutdown).
static thread_local PJ_CONTEXT* tl_proj_ctx = nullptr;

PJ_CONTEXT* proj_get_context() {
    if (!tl_proj_ctx) {
        tl_proj_ctx = proj_context_create();
        // Explicitly disable on-demand CDN grid downloads. PROJ 7+ honours
        // the PROJ_NETWORK env var and a global default toggled at build
        // time; in a sandboxed Qore program that's an SSRF surface, so pin
        // it off per-context regardless of environment.
        if (tl_proj_ctx) {
            proj_context_set_enable_network(tl_proj_ctx, 0);
        }
    }
    return tl_proj_ctx;
}

// hashdecl pointer — qpp generates code that assigns this, but doesn't declare it.
const TypedHashDecl* hashdeclProjVersionInfo = nullptr;

// NOTE: the class pointer QC_PROJTRANSFORMER and id CID_PROJTRANSFORMER are
// DEFINED by qpp in the generated QC_ProjTransformer.cpp — do not declare them
// here or the link step produces duplicate-symbol errors.

QoreNamespace PNS("Qore::PROJ");

static void proj_module_init(QoreModuleInitContext& ctx, ExceptionSink& xsink) {
    // hashdecls first (referenced by functions below)
    hashdeclProjVersionInfo = init_hashdecl_ProjVersionInfo(PNS);
    // classes
    QC_PROJTRANSFORMER = initProjTransformerClass(PNS);
    PNS.addSystemClass(QC_PROJTRANSFORMER);
    // standalone functions last
    init_proj_functions(PNS);
}

static void proj_module_ns_init(QoreNamespace* rns, QoreNamespace* qns, ExceptionSink& xsink) {
    qns->addNamespace(PNS.copy());
}

static void proj_module_delete() {
}
