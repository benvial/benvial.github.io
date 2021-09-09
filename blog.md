---
layout: page
title: Blog
weight: 7
---
<!-- <h2>Latest Posts</h2> -->

<ul>
  {% for post in site.posts %}
    <li>
      <h3><a href="{{ post.url }}">{{ post.title }}</a></h3>
      <p>{{ post.date  | date_to_string }}</p>
    </li>
    <hr>
  {% endfor %}
</ul>
