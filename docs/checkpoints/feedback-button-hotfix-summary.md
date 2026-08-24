# Multi-Agent feedback button hotfix

- Delegated click handling now catches `#reviewReturnRevision`, so the action survives live chatbox re-renders.
- Blank Owner feedback with an existing external review persists the default instruction `Use the external review as feedback for the next pass.` as an `OWNER_REVISION` artifact before starting the native feedback pass.
- No inventory mutation or authority expansion.
