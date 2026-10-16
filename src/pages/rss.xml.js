import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { site } from "@/data/site";

export async function GET(context) {
  const posts = (await getCollection("posts")).sort(
    (a, b) => new Date(b.data.pubDate).valueOf() - new Date(a.data.pubDate).valueOf()
  );
  return rss({
    title: `${site.name} (writing)`,
    description: site.description,
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: new Date(post.data.pubDate),
      link: `/blog/posts/${post.id}/`,
      categories: post.data.tags,
    })),
  });
}
