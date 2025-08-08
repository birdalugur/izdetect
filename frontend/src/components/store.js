import { writable } from "svelte/store";

export const cameraUrls = writable({ cameraUrl1: "", cameraUrl2: "" });

export const SERVER_IP = "http://10.100.17.151"

// Dark mode store
export const darkMode = writable(false);
export const detectionRefresh = writable(0);
export const modalStore = writable({
  isOpen: false,
  component: null,
  props: {}
});

// Modal yönetimi için yardımcı fonksiyonlar
modalStore.openModal = function (component, props = {}, isSmallModal = false) {
  modalStore.set({
    isOpen: true,
    component: component,
    props: props,
    isSmallModal: isSmallModal
  });
};

modalStore.closeModal = function () {
  modalStore.set({
    isOpen: false,
    component: null,
    props: {}
  });
};

export function clearCameraUrls() {
  cameraUrls.set({ cameraUrl1: "", cameraUrl2: "" });
}
