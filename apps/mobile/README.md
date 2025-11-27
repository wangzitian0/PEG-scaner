# PEG Scanner Mobile Application

This directory contains the React Native application for the PEG Scanner project. It provides the user interface for interacting with stock information, factor calculations, and the AI-powered conversational agent.

## How to Run

To run the mobile application, navigate to this directory and follow the standard React Native development procedures.

**Prerequisites:**
*   Node.js and npm/yarn
*   React Native development environment setup (including Android Studio, Xcode, CocoaPods for iOS)

**Commands (Example - may vary based on specific setup):**

```bash
# Install dependencies
npm install # or yarn install

# Type-check the React Native codebase
npx nx run mobile:typecheck

# Run on iOS (requires CocoaPods and Xcode)
npx react-native run-ios

# Run on Android (requires Android Studio and emulator/device)
npx react-native run-android
```

## Single Stock Page

- The home screen now includes the single-stock detail module that fetches data via GraphQL (`/graphql`, schema in `libs/schema/schema.graphql`).
- You can deep-link directly to a ticker using the `symbol` query param, e.g. `http://localhost:5173/?symbol=AAPL`.
- Use the “Load” input on the UI to jump to any symbol (even if it’s not currently listed in the PEG watchlist). The query param updates automatically so the page can be bookmarked or shared.
