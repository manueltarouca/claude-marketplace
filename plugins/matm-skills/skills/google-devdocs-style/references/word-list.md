# Word list

The long tail. SKILL.md carries the words you hit on almost every document; this file covers
the rest. Canonical source: [Google's word list](https://developers.google.com/style/word-list).

## Contents

- [Words whose meaning matters](#words-whose-meaning-matters)
- [Inclusive language](#inclusive-language)
- [Violent and ableist terms](#violent-and-ableist-terms)
- [Anthropomorphism](#anthropomorphism)
- [Wordiness](#wordiness)
- [Technical terms people get wrong](#technical-terms-people-get-wrong)

## Words whose meaning matters

These are not style preferences. Each one makes a different promise to the reader, and
picking the wrong one changes what the documentation commits to.

| Word | Means | Use it for |
|---|---|---|
| `must` | required | A step that fails without it |
| `should` | recommended, not required | The advised path when alternatives exist |
| `can` | able to | Capability and permission |
| `might` | possible | Genuinely uncertain outcomes |
| `we recommend` | Google's advice | Recommendations, in place of "you should" |

Reserve `will` for genuine future events. Most of the time the present tense is correct and
`will` is padding: the API `returns` a token, it does not `will return` one.

## Inclusive language

| Avoid | Use |
|---|---|
| blacklist, whitelist | denylist, allowlist, blocklist |
| master, slave | primary, main, original, parent, controller, replica, worker |
| grandfathered | legacy status, exempt |
| man hours, manpower | person hours, staffing |
| he, she, as a generic | they |
| guys, as a group | everyone, folks, all |
| native, for built-in | built-in |

## Violent and ableist terms

| Avoid | Use |
|---|---|
| abort | stop, cancel, end, exit |
| kill | stop, end, force quit |
| hang | stop responding |
| crash, for user error | fail, stop responding |
| sanity check | quick check, confidence check, validation |
| dummy value | placeholder, sample |
| crazy, insane, lame | complex, unexpected, baffling |
| cripple | degrade, disable |
| blind to | unaware of, ignores |

Keep the literal term when it names a real API: `SIGKILL` and `kill(1)` stay as they are.
The rule covers your prose, not the system's vocabulary.

## Anthropomorphism

Software does not want, think, know, or see. Attributing intent obscures the mechanism,
which is the thing the reader came for.

| Avoid | Use |
|---|---|
| the parser wants a string | the parser expects a string |
| the API knows about your project | the API reads your project ID |
| the field displays | the field appears, the console displays the field |
| the service is smart enough to retry | the service retries |

`display` is transitive. Something displays a thing; a thing does not "display".

## Wordiness

| Avoid | Use |
|---|---|
| due to the fact that | because |
| in the event that | if |
| at this point in time | now, or delete |
| a number of | many, or the number |
| is able to | can |
| has the ability to | can |
| make use of | use |
| perform a query | query |
| in a timely manner | quickly, or the deadline |
| it is possible to | you can |

## Technical terms people get wrong

| Avoid | Use |
|---|---|
| CLI tool | CLI, or command-line tool |
| API interface | API |
| login, as a verb | log in, sign in |
| setup, as a verb | set up |
| backend, frontend, as two words | backend, frontend |
| repo, in reference docs | repository |
| auth, in reference docs | authentication, authorization, whichever you mean |
| deprecated, for removed | removed, if it is gone |

Say which one you mean when a word covers two ideas. "Auth" hides the difference between
proving who you are and being allowed to do something, and readers debugging a 403 need
exactly that difference.
