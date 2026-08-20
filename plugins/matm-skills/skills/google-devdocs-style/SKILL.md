---
name: google-devdocs-style
description: Apply the Google developer documentation style guide to technical writing. Enforces second person, active voice, present tense, sentence-case headings, conditions before instructions, and cuts words that undermine the reader ("simply", "just", "allows you to"). Use when writing or revising a README, CLAUDE.md or AGENTS.md, API reference, code comment, error or log message, CLI help text, changelog, runbook, or setup instructions, including when the request is only "write the README", "document this module", or "word this error better" and says nothing about style. Also use when asked to make documentation clearer or more consistent. For conversational prose, chat replies, posts, and marketing copy, use the unslop skill instead.
---

# Google developer documentation style

Rewrite technical documentation to follow the [Google developer documentation style
guide](https://developers.google.com/style). The target is documentation a stranger can act
on without asking you a follow-up question.

Fetch the canonical page when a specific question comes up rather than guessing at a rule
you can look up.

## Scope

This skill owns technical artifacts: READMEs, agent instruction files (CLAUDE.md,
AGENTS.md), API references, docstrings, code comments, error and log messages, CLI help
text, release notes, changelogs, migration guides, runbooks, and setup instructions.

Conversational prose belongs to the `unslop` skill, which strips AI tells. This one imposes
a house style. When both apply, style the document here and let `unslop` handle the
surrounding commentary.

## The four rules that change the most text

Most of the improvement comes from these, so apply them first.

**Second person.** Address the reader as "you", not "we", not "the user". Use the imperative
for instructions, because a step is something the reader does.

- Yes: `To deploy, run terraform apply.` and `You need a service account.`
- No: `We can now deploy the stack.` and `The user must create a service account.`

**Active voice.** Name the actor. Passive voice hides who is responsible, which matters most
in exactly the sentences where the reader needs to know whether they have to act.

- Yes: `The scheduler retries the job three times.`
- No: `The job is retried three times.`

**Present tense.** Describe what the software does, not what it will do. Future tense makes
the behavior sound hypothetical.

- Yes: `The build fails if the lockfile is out of date.`
- No: `The build will fail if the lockfile is out of date.`

**Sentence case in every heading and title.** Capitalize the first word and proper nouns
only. This one is mechanical and it is the most visible marker of the style.

- Yes: `## Configure the webhook`
- No: `## Configure The Webhook`

## Words that cost you the reader

The worst offenders comment on difficulty. A reader stuck on the step you called "simple"
now has two problems. Cut these; they carry no information.

| Avoid | Use |
|---|---|
| simply, easily, just, obviously, of course, straightforward | delete the word |
| please, in instructions | delete it, the imperative is already polite |
| allows you to, enables you to | lets you |
| in order to | to |
| leverage, utilize | use |
| e.g., i.e. | for example, that is |
| etc. | name the remaining items or rewrite |
| note that, it should be noted | delete it and state the fact |
| and/or | say which one you mean |
| desired | wanted, needed |
| via | through, by using |

Read `references/word-list.md` when editing a document heavy in jargon, or when you are
unsure whether a term is on the list. It covers inclusive-language replacements and the
words whose meaning shifts (`should` against `must` against `can`), which the table above
leaves out.

Write standard American spelling.

## Structure

**Put conditions before instructions.** A reader needs to know whether a step applies before
they start it, otherwise they act and then discover they should not have.

- Yes: `If you use a custom domain, add a CNAME record.`
- No: `Add a CNAME record if you use a custom domain.`

**Put the goal before the action**, for the same reason.

- Yes: `To rotate the key, run gcloud kms keys versions create.`
- No: `Run gcloud kms keys versions create to rotate the key.`

**Mark optional steps** with a literal `Optional:` prefix.

**Number a list only when order matters.** Numbering promises a sequence. Use bullets for
everything else.

**Use serial commas**, as in `a, b, and c`.

## Code, UI, and links

- Put literals in code font: file names, commands, flags, values, types, function names.
- Put UI element names in bold, as in **Save** or **File > New > Document**.
- Write descriptive link text. `click here` and `read more` tell a reader scanning the page,
  or a screen reader listing links, nothing at all.
- Use meaningful placeholders in caps, such as `PROJECT_ID` rather than `foo` or `dummy`.
- Name the target instead of its position. "Above", "below", and "on the right" break when
  layout changes and mean nothing in a screen reader.

## Error and log messages

An error message has one job: get the reader unstuck. Answer what happened, why, and what to
do next. That last part is the one most messages omit and the only one the reader needs.

- Yes: `Can't parse config.yaml: line 12 expects a string, found a list. Quote the value or
  remove the list.`
- No: `Invalid configuration!` or `Something went wrong.` or `Error: unexpected token`

State the problem rather than assigning fault, skip the apology, and skip exclamation points.
Prefer the positive form, since `Can't parse` reads faster than `Failed to not reject`.

## Timeless documentation

Cut words that only make sense on the day you wrote them: "currently", "new", "recently",
"now", "at this time", "will soon". A doc that calls a feature "new" is wrong within a year
and nobody notices. State the behavior, not its novelty. Leave unreleased work out of
reference documentation.

## Agent instruction files

CLAUDE.md and AGENTS.md are documentation for a reader that follows instructions literally,
so the same rules hold with two adjustments. Keep the imperative throughout, since these
files are almost entirely directives. And give the reason behind a rule rather than reaching
for bold and "always", because an agent that knows why a rule exists applies it to the case
you did not anticipate.

## How to work

When editing existing text, keep the author's meaning and technical claims intact. This is a
style pass. If a sentence is wrong on the facts, say so instead of quietly rewriting it.

Match the artifact's own conventions on top of the style: a changelog groups by release and
category, a README opens with what the thing is and how to run it, a runbook opens with the
symptom.

You are done when every heading is sentence case, every instruction addresses the reader in
the imperative, every sentence naming an actor uses active voice and present tense, and no
word from the avoid list survives.
