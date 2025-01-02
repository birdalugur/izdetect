import { writable } from "svelte/store";

export const cameraUrls = writable({ cameraUrl1: "", cameraUrl2: "" });

export function clearCameraUrls() {
    cameraUrls.set({ cameraUrl1: "", cameraUrl2: "" });
}
