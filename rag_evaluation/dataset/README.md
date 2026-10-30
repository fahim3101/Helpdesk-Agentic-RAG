# Evaluation Dataset

This directory contains the evaluation dataset used to assess the Agentic RAG helpdesk workflow.

## Dataset format

Each row contains:

- `user_input`: the question asked by the employee or user
- `reference`: the expected answer based on the relevant company documentation

The current dataset is intentionally small and illustrative. It is designed to be a realistic first-pass evaluation set for a helpdesk scenario.

## Important note

The question and reference examples are based on the sample knowledge base in this repository and should be replaced with verified internal policy text before serious production evaluation.

Do not treat these examples as official company policy.
