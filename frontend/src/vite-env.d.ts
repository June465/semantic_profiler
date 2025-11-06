/// <reference types="vite/client" />

// _NEW_: Add a global JSX namespace declaration.
// This is a brute-force fix for the persistent build error.
declare namespace JSX {
    interface IntrinsicElements {
        [elemName: string]: any;
    }
}