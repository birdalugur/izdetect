import App from './App.svelte';
import './App.css'; // TailwindCSS'in yer aldığı dosya



const app = new App({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default app;