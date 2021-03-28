<script>
	import { onMount } from "svelte";

	export let name;
	let the_data = null;
	onMount(async () => {
		const res = await fetch("api/binance_assets");
    	the_data = await res.json();
		the_data = the_data["res"]
	})

</script>

<main>
	<section class="section">
		<div class="container">
		  <h1 class="title">
			Hello World
		  </h1>
		  <p class="subtitle">
			My first website with <strong>Bulma</strong>!
		  </p>
		</div>
	  </section>
	<h1>Hello {name}!</h1>
	<h2>Here data: {JSON.stringify(the_data)}</h2>
	
	<table>
		<th>Symbol</th>
		<th>Amount</th>
			{#if the_data != null}
				{#each the_data as k}
				<tr>
					<td>{k.asset}</td>
					<td>{k.free}</td>
				</tr>
				{/each}
			{/if}
	</table>
	<p></p>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>