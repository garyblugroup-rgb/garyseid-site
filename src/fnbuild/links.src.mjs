// Short-link service for garyseid.com
// GET  /s/<slug>   -> 302 redirect to the stored destination
// POST /api/links  -> admin API: {action: create|list|delete, key, slug, url, overwrite}
// Requires the LINKS_KEY environment variable (the admin passphrase).
import { getStore } from '@netlify/blobs';

const SITE = 'https://www.garyseid.com';
const RESERVED = ['go', 's', 'api', 'links', 'intake', 'thanks'];

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });

export default async (req) => {
  const url = new URL(req.url);
  const store = getStore('shortlinks');

  // Redirect: /s/<slug>
  if (url.pathname.startsWith('/s/')) {
    const slug = url.pathname.slice(3).replace(/\/+$/, '').toLowerCase();
    if (slug) {
      const dest = await store.get('l:' + slug);
      if (dest) return new Response(null, { status: 302, headers: { location: dest } });
    }
    return new Response('That short link does not exist. Visit ' + SITE, {
      status: 404, headers: { 'content-type': 'text/plain' }
    });
  }

  // Admin API: /api/links
  if (url.pathname === '/api/links') {
    if (req.method !== 'POST') return json({ error: 'POST only.' }, 405);
    const KEY = process.env.LINKS_KEY;
    if (!KEY) return json({ error: 'Setup needed: the LINKS_KEY environment variable is not set in Netlify.' }, 500);
    let body;
    try { body = await req.json(); } catch { return json({ error: 'Bad request.' }, 400); }
    if (!body || body.key !== KEY) return json({ error: 'Wrong passphrase.' }, 403);

    if (body.action === 'create') {
      const slug = String(body.slug || '').trim().toLowerCase();
      const dest = String(body.url || '').trim();
      if (!/^[a-z0-9-]{1,60}$/.test(slug)) return json({ error: 'Short name: letters, numbers and dashes only (max 60).' }, 400);
      if (RESERVED.includes(slug)) return json({ error: 'That name is reserved. Pick another.' }, 400);
      if (!/^https?:\/\/.+/.test(dest)) return json({ error: 'Destination must be a full link starting with https://' }, 400);
      const existing = await store.get('l:' + slug);
      if (existing && !body.overwrite) return json({ error: 'exists', existing }, 409);
      await store.set('l:' + slug, dest);
      return json({ ok: true, short: SITE + '/s/' + slug });
    }

    if (body.action === 'list') {
      const { blobs } = await store.list({ prefix: 'l:' });
      const items = [];
      for (const b of blobs) {
        const u = await store.get(b.key);
        items.push({ slug: b.key.slice(2), url: u || '' });
      }
      items.sort((a, b2) => a.slug.localeCompare(b2.slug));
      return json({ ok: true, items });
    }

    if (body.action === 'delete') {
      const slug = String(body.slug || '').trim().toLowerCase();
      await store.delete('l:' + slug);
      return json({ ok: true });
    }

    return json({ error: 'Unknown action.' }, 400);
  }

  return new Response('Not found.', { status: 404 });
};

export const config = { path: ['/s/*', '/api/links'] };
