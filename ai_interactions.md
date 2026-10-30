# AI Interactions Log

## Agentic Workflow

The user's actual request was: "do what the pdf says then psuh it to github pls", following a link to the CodePath starter repository and an attached assignment PDF.

Codex read all 13 rendered PDF pages, inspected the starter, researched filtering concepts using Google's and YouTube's official documentation, and implemented the core project. It expanded the catalog from 10 to 18 fictional tracks, completed the functional and object interfaces, fixed the module import, added CLI profiles and a weight experiment, wrote tests, and captured real terminal output in the README. It completed the model card and prepared the fork for publication.

The default design uses genre 2, mood 1, energy similarity 1, and optional acoustic similarity 0.5. The experiment uses genre 1 and energy 2. This is configuration through an immutable weights dataclass; a full Strategy pattern was not necessary for the core assignment. Optional extension challenges are not claimed as completed.

Verification was performed by the agent with pytest and CLI executions. No manual human checks or listening sessions have been reported. The personal reflection is explicitly an AI-assisted draft requiring author review. No additional user prompts, separate AI chats, personal reactions, or human edits have been invented for this log.

## Design reasoning and review

The feature selection favors interpretable labels and energy closeness. The profile was critiqued as sufficient for distinguishing intense rock from chill lofi but too narrow for complex tastes. Adversarial profiles expose genre dominance and absent catalog coverage. The score and ranking are separate so their responsibilities can be tested independently; both public APIs reuse the same logic to avoid inconsistent results.

The baseline and weight-shift outputs were run and compared, not predicted and presented as observations. Research links appear in the README. The uploaded PDF and its account-specific page information were not copied into the public repository.
