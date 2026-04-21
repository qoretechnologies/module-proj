/* -*- mode: c++; indent-tabs-mode: nil -*- */
/*
    QC_ProjTransformer.h

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

#ifndef _QORE_QC_PROJTRANSFORMER_H
#define _QORE_QC_PROJTRANSFORMER_H

#include "proj-module.h"

#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>

// Coordinate transformer between two coordinate reference systems.
//
// Thread-safety model: the Qore-level object is reusable across threads.
// Internally we cache one `PJ*` per thread, built lazily on first use in
// that thread using the thread's own `PJ_CONTEXT*`. PROJ requires each PJ
// to be used only with the context it was created under, hence per-thread
// objects.
class QoreProjTransformer : public AbstractPrivateData {
public:
    DLLLOCAL QoreProjTransformer(const char* src, const char* tgt,
            bool normalize_for_visualization, ExceptionSink* xsink);
    DLLLOCAL virtual ~QoreProjTransformer();

    // Get or lazily build a PJ* for the calling thread.
    // Returns nullptr and raises an exception on failure.
    DLLLOCAL PJ* getPj(ExceptionSink* xsink);

    DLLLOCAL const std::string& sourceCrs() const { return source_crs; }
    DLLLOCAL const std::string& targetCrs() const { return target_crs; }
    DLLLOCAL bool isNormalized() const { return normalized; }

private:
    std::string source_crs;
    std::string target_crs;
    bool normalized;

    // per-thread PJ* cache; each entry holds (ctx, pj) so we can destroy
    // the PJ with its matching context when the transformer is freed.
    struct ThreadEntry {
        PJ_CONTEXT* ctx;
        PJ* pj;
    };
    std::mutex cache_mutex;
    std::unordered_map<std::thread::id, ThreadEntry> pj_cache;
};

#endif
