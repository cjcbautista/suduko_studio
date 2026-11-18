# Copilot evidence screenshots

The rubric requires evidence from the student's own GitHub Copilot session. Do not fabricate or submit generated conversations. Open this repository in VS Code with GitHub Copilot enabled, use the prompts in `prompts.json`, and capture both the prompt and meaningful response.

Save these files here:

1. `copilot_testing_framework.png` — prompt/response for setting up pytest.
2. `copilot_unique_solution.png` — prompt/response for proving one unique solution.
3. `copilot_top_10.png` — prompt/response for local Top 10 logic.
4. `copilot_grid_styling.png` — prompt/response for alternating 3×3 colors.
5. `copilot_rejected_suggestion.png` — evidence of evaluating or rejecting a suggestion.

A strong rejection example is the prompt about sending the entire solution to the browser. Record that the proposal was rejected because it exposes answer data; the implemented design keeps the solution server-side and exposes only game-ID-backed Check and Hint endpoints.

## Capture checklist

- Show enough of the VS Code window to identify Copilot Chat.
- Keep the complete prompt visible.
- Include the relevant response, not only a completion toast.
- If code was accepted, show the resulting file or test output in a second image if needed.
- Redact account names, tenant details, tokens, or paths that contain personal information.
- Do not claim suggestions were accepted if you rewrote or rejected them; document the decision accurately.
