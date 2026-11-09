// The only bridge between HTML screens and the Phaser scene.
export const bus = new EventTarget();
export const emit = (name, detail) => bus.dispatchEvent(new CustomEvent(name, { detail }));
export const on = (name, fn) => bus.addEventListener(name, event => fn(event.detail));
