---
title: "Search"
layout: default
description: "Search all CDC Influenza Division resources including full-text content from PDFs and linked pages."
permalink: /search/
---

<div class="container pb-6 pt-6 pt-md-10 pb-md-10" data-pagefind-ignore>
  <div class="row justify-content-start">
    <div class="col-12 col-md-10">
      <h1 class="title">Search Resources</h1>
      <p>Search across all resource pages and full-text content extracted from PDFs and linked documents.</p>
      <div id="search"></div>
    </div>
  </div>
</div>

<link href="{{ '/pagefind/pagefind-ui.css' | relative_url }}" rel="stylesheet">
<script src="{{ '/pagefind/pagefind-ui.js' | relative_url }}"></script>
<script>
  window.addEventListener('DOMContentLoaded', function () {
    var pf = new PagefindUI({
      element: "#search",
      showSubResults: true,
      showImages: false,
      processResult: function (result) {
        if (result.meta && result.meta.url) {
          result.url = result.meta.url;
        }
        if (result.meta && result.meta.title) {
          result.meta.title = result.meta.title.split(', category:')[0];
        }
        return result;
      }
    });
    // Pre-fill from ?q= query param (from header search box)
    var params = new URLSearchParams(window.location.search);
    var q = params.get('q');
    if (q) {
      pf.triggerSearch(q);
    }
  });
</script>
