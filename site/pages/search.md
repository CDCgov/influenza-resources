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

<link href="/pagefind/pagefind-ui.css" rel="stylesheet">
<script src="/pagefind/pagefind-ui.js"></script>
<script>
  window.addEventListener('DOMContentLoaded', function () {
    new PagefindUI({
      element: "#search",
      showSubResults: true,
      showImages: false,
      processTerm: function (term) { return term; }
    });
  });
</script>
