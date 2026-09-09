# Side Project Generator

A tiny app that smashes together a random niche, a random audience, and a random app mechanic — so you have something concrete to build instead of staring at a blank page.

## What it does

Ever want to start a side project but can't think of *what* to build? This app randomly generates an idea for you, shown as a simple formula:

**Domain × User × Mechanic**

- **Domain** — a topic or niche (e.g. "Home Fermenting," "Bird Watching," "Splitting Costs")
- **User** — who it's for (e.g. "Night Owls," "Retirees," "Shift Workers")
- **Mechanic** — the core way people interact with it (e.g. "Daily Puzzle," "Streak Shield")

Put them together and you've got a project prompt, like: *a daily puzzle for retirees, in the bird watching space.* It won't design the app for you, but it gives you a starting point that's specific enough to actually run with.

There's no AI involved. It picks one item from each of three lists, then checks the three actually work together. Simple on purpose.

## How it works

1. Click **Generate**.
2. The app rolls one Domain, one User, and one Mechanic and drops them into the three fields on screen.
3. Hover over any field to see a one-sentence explanation of what that entry actually means, in case the name alone isn't obvious.

That's the whole app — one button, one action. Click it again for a completely new combination.

### Why the combinations aren't fully random

Rolling three lists independently produces a lot of gibberish: the same idea appearing twice, an audience that has nothing to do with the topic, or a mechanic with nothing to operate on. So every entry carries tags, and a roll has to pass three rules:

1. **The domain can't restate the user.** Couples never gets paired with Relationships.
2. **The topic has to matter to the audience.** Every domain and user carries `themes`, and they must share at least one. Community Growing and Freelancers have nothing in common, so that pair never comes up.
3. **The pairing has to support the mechanic.** Mechanics declare what they `require` and the domain and user together declare what they `afford`. Reverse Trivia needs a body of `facts` behind it. NFC Unlock needs `place` and `things`.

About three quarters of domain and user pairs survive rule 2, so the idea space stays wide.

Tick **Chaos mode** under the button to drop rules 2 and 3 and roll deliberately strange combinations. Rule 1 always applies, so you never get the same idea twice in one prompt.

## Getting started

You'll need Python and pip installed.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run main.py
```

Streamlit will print a local URL in your terminal (usually `http://localhost:8501`) — open that in your browser.

No API keys, accounts, or configuration needed. It runs entirely on your machine using local data.

## Hosting

The app is deployed on [Streamlit Community Cloud](https://streamlit.io/cloud), which deploys straight from this GitHub repo (private repos are supported once you authorize Streamlit's GitHub App on it). Point it at `main.py` on the `main` branch; it reads `requirements.txt` to build the environment and redeploys automatically on push.

## Project structure

| File | What it's for |
|---|---|
| `main.py` | Layout, styling, and the Streamlit widgets |
| `combos.py` | Loads the data and picks a combination that passes the rules |
| `scripts/validate_data.py` | Checks the data files for mistakes |
| `data/domains.json` | Possible domains, each with `themes` and `affords` |
| `data/users.json` | Possible audiences, each with `themes`, `affords`, and `avoid_domains` |
| `data/mechanics.json` | Possible mechanics, each with `requires` |
| `data/tags.json` | The tag vocabulary, with a one-line meaning for each tag |
| `.streamlit/config.toml` | The app's dark theme and accent color |
| `requirements.txt` | Python dependencies, used locally and by the hosting platform |

## Customizing

Want different ideas to come out? Edit the JSON files in `data/`. Every entry needs a name, a `description` for the tooltip, and its tags:

```json
{
  "domain": "Home Baking",
  "description": "Baking bread, cakes, pastries, and desserts with more confidence",
  "themes": ["food", "making"],
  "affords": ["things", "craft", "routine", "facts"]
}
```

- **`themes`** say what the entry is about. Pick from the themes in `data/tags.json`. Keep them to subject matter, not life circumstance, or unrelated things start matching.
- **`affords`** say what a domain or user brings to the table. A mechanic's **`requires`** must be covered by the domain and user combined.
- **`avoid_domains`** on a user lists domain slugs that would just restate that audience, like Homebrewers and Home Fermenting. A slug is the name lowercased with dashes.

After editing, run the checker:

```bash
python scripts/validate_data.py
```

It fails on unknown tags, missing fields, duplicate names, and any entry that ends up in no valid combination. It also warns when two names look like the same idea, which is how the old list ended up with both Freelancers and Freelance Groups.

No code changes required — the app reads these files fresh each time it runs.
