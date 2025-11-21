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

## Proto Integration

- The mobile app consumes the ping response defined in `schema/stock.proto`. A JSON descriptor generated via `npx pbjs -t json` lives under `mobile/src/proto/stock_descriptor.json`.
- Protobuf decoding uses `protobufjs` with the descriptor to ensure the UI reflects the exact backend payload.
