<script>
	import { io } from 'socket.io-client';
	import { spring } from 'svelte/motion';

	let loadingProgress = spring(0, {
		stiffness: 0.05
	});

	import { goto } from '$app/navigation';
	import {
		USAGE_POOL,
		WEBUI_NAME,
		activeUserCount,
		config,
		mobile,
		socket,
		theme,
		user
	} from '$lib/stores';
	import { onMount, setContext, tick } from 'svelte';
	import { Toaster, toast } from 'svelte-sonner';

	import { getBackendConfig } from '$lib/apis';
	import { getSessionUser } from '$lib/apis/auths';

	import '../app.css';
	import '../tailwind.css';

	import 'tippy.js/dist/tippy.css';

	import { WEBUI_BASE_URL } from '$lib/constants';
	import i18n, { getLanguages, initI18n } from '$lib/i18n';

	const pathname = window.location.pathname;
	const isChat = pathname.startsWith('/chat');
	const isAuth = pathname.startsWith('/auth');

	setContext('i18n', i18n);

	let loaded = false;
	const BREAKPOINT = 768;

	onMount(async () => {
		theme.set(localStorage.theme);

		mobile.set(window.innerWidth < BREAKPOINT);
		const onResize = () => {
			if (window.innerWidth < BREAKPOINT) {
				mobile.set(true);
			} else {
				mobile.set(false);
			}
		};

		window.addEventListener('resize', onResize);

		let backendConfig = null;
		try {
			backendConfig = await getBackendConfig();
			console.log('Backend config:', backendConfig);
		} catch (error) {
			console.error('Error loading backend config:', error);
		}
		// Initialize i18n even if we didn't get a backend config,
		// so `/error` can show something that's not `undefined`.

		const languages = await getLanguages();

		const browserLanguage = navigator.languages
			? navigator.languages[0]
			: navigator.language || navigator.userLanguage;

		initI18n(languages.includes(browserLanguage) ? browserLanguage : backendConfig?.default_locale);

		if (backendConfig) {
			// Save Backend Status to Store
			await config.set(backendConfig);
			await WEBUI_NAME.set(backendConfig.name);

			if ($config) {
				const _socket = io(`${WEBUI_BASE_URL}`, {
					path: '/ws/socket.io',
					auth: { token: localStorage.token }
				});

				_socket.on('connect', () => {
					console.log('connected');
				});

				await socket.set(_socket);

				_socket.on('user-count', (data) => {
					console.log('user-count', data);
					activeUserCount.set(data.count);
				});

				_socket.on('usage', (data) => {
					console.log('usage', data);
					USAGE_POOL.set(data['models']);
				});

				if (isAuth) {
					localStorage.removeItem('token');
					localStorage.removeItem('isChat');
					await goto('/auth');
				} else if (isChat || localStorage.token) {
					let authToken;
					if (isChat) {
						console.log('isChat');
						authToken =
							'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjkzYjE1ZWI4LTJiY2QtNDJmMS1hYTRiLTFlNGQ1M2FlMjhiNyJ9.JjbDVgFjf0D8YXwoJxO3tq_xRmnY9-9r5KG64hZ8HFs';
					} else {
						authToken = localStorage.token;
					}

					// Get Session User Info
					const sessionUser = await getSessionUser(authToken).catch((error) => {
						toast.error(error);
						return null;
					});

					if (isChat) {
						localStorage.setItem('token', authToken);
						localStorage.setItem('isChat', 'true');
						await user.set(sessionUser);
						await goto('/');
					} else if (sessionUser) {
						// Save Session User to Store
						await user.set(sessionUser);
					} else {
						// Redirect Invalid Session User to /auth Page
						localStorage.removeItem('token');
						localStorage.removeItem('isChat');
						await goto('/auth');
					}
				} else {
					await goto(isChat ? '/' : '/auth');
				}
			}
		} else {
			// Redirect to /error when Backend Not Detected
			await goto(`/error`);
		}

		await tick();

		if (
			document.documentElement.classList.contains('her') &&
			document.getElementById('progress-bar')
		) {
			loadingProgress.subscribe((value) => {
				const progressBar = document.getElementById('progress-bar');

				if (progressBar) {
					progressBar.style.width = `${value}%`;
				}
			});

			await loadingProgress.set(100);

			document.getElementById('splash-screen')?.remove();

			const audio = new Audio(`/audio/greeting.mp3`);
			const playAudio = () => {
				audio.play();
				document.removeEventListener('click', playAudio);
			};

			document.addEventListener('click', playAudio);

			loaded = true;
		} else {
			document.getElementById('splash-screen')?.remove();
			loaded = true;
		}

		return () => {
			window.removeEventListener('resize', onResize);
		};
	});
</script>

<svelte:head>
	<title>{$WEBUI_NAME}</title>
	<link crossorigin="anonymous" rel="icon" href="{WEBUI_BASE_URL}/static/favicon.png" />

	<!-- rosepine themes have been disabled as it's not up to date with our latest version. -->
	<!-- feel free to make a PR to fix if anyone wants to see it return -->
	<!-- <link rel="stylesheet" type="text/css" href="/themes/rosepine.css" />
	<link rel="stylesheet" type="text/css" href="/themes/rosepine-dawn.css" /> -->
</svelte:head>

{#if loaded}
	<slot />
{/if}

<Toaster richColors position="top-center" />
