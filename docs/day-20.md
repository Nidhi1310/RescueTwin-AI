# Day 20 — Report export

Day 20 makes the generated incident report usable outside the dashboard without changing report-generation behavior.

## Changes

- Added a Copy action for generated incident reports.
- Added a Download action that saves the same report content as a `.txt` file.
- Download filenames include the active rainfall scenario and incident zone.
- Added user feedback after copy/download actions.
- Preserved the existing generated report content and backend response format.

## Verification

Run the frontend production build with:

```powershell
npm.cmd run build
```

Then select a flood zone, generate an incident report, and verify both Copy and Download actions use the displayed report content.
