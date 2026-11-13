"""Smoke test for index.html with a mocked Claude runtime.

Usage: python3 tests/smoke_test.py [path/to/index.html] [chrome-executable]
Needs: pip install playwright (and a Chromium/Chrome binary).

The mock `window.claude.use("sample")` echoes prompts, so this checks UI flow
and context isolation, not answer quality. db/user resolve null, so the page
falls back to localStorage.
"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "index.html"))
CHROME = sys.argv[2] if len(sys.argv) > 2 else None

MOCK = """
window.__calls = [];
window.claude = { use: async (n) => {
  if (n !== 'sample') return null;
  return async (input, opts) => {
    window.__calls.push(input);
    const t = typeof input === 'string' ? 'SUMMARY: ' + input.slice(0, 30) : 'Reply #' + window.__calls.length;
    if (opts && opts.onText) opts.onText({ text: t, delta: t });
    return { text: t, truncated: false };
  };
}};
"""

async def run(browser, width):
    pg = await browser.new_page(viewport={"width": width, "height": 800})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    await pg.route("**/cdnjs.cloudflare.com/**", lambda r: r.abort())  # markdown libs optional
    await pg.add_init_script(MOCK)
    await pg.goto("file://" + PAGE)
    await pg.wait_for_timeout(400)

    async def say(text):
        await pg.fill("#input", text); await pg.click("#send"); await pg.wait_for_timeout(200)

    await say("Root question")
    # Branch with a Claude summary passed down
    await pg.click("#aBranch"); await pg.check("input[value=summary]"); await pg.click("#mOk"); await pg.wait_for_timeout(300)
    await say("Side question")
    calls = await pg.evaluate("window.__calls")
    branch_prompt = json.dumps(calls[-1])
    assert "<inherited_context mode=\\\"summary\\\">" in branch_prompt, "child should get summary context"
    assert "Reply #1" not in branch_prompt, "child must not see parent's raw reply (isolation)"

    # Cross-node pass to root (summary), then merge up
    await pg.click("#aSend"); await pg.click("#mOk"); await pg.wait_for_timeout(200); await pg.click("#mOk"); await pg.wait_for_timeout(200)
    await pg.click("#aClose"); await pg.click("#mOk"); await pg.wait_for_timeout(300); await pg.click("#mOk"); await pg.wait_for_timeout(300)
    root_text = await pg.inner_text("#msgs")
    assert "PASSED FROM" in root_text.upper() and "MERGED UP FROM" in root_text.upper(), "root should show pass + merge notes"
    assert await pg.locator(".tnode").count() == 1, "closed branch should be removed"
    assert not errors, errors
    await pg.close()
    print(f"ok  width={width}")

async def main():
    async with async_playwright() as p:
        kw = {"executable_path": CHROME} if CHROME else {}
        b = await p.chromium.launch(**kw)
        for w in (1200, 390):
            await run(b, w)
        await b.close()

asyncio.run(main())
