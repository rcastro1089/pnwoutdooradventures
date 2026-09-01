import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string().max(60),
    description: z.string().min(120).max(160),
    pubDate: z.date(),
    keyword: z.string(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
