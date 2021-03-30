<script>
	import { onMount, onDestroy } from "svelte";

	export let name;
	let scheduler = null;
	let binance_assets = null;
	let pancake_lp = null;

	async function get_api_data () {
		var res = await fetch("api/binance_assets");
    	binance_assets = await res.json();
		binance_assets = binance_assets["res"]
		
		res = await fetch("api/get_pancake_liquidity_pool");
		pancake_lp = await res.json();
		pancake_lp = pancake_lp["res"]
	}

	onMount(async () => {
		get_api_data()
		if (scheduler == null) {
			scheduler = setInterval(get_api_data, 5000)
		}
	})

	onDestroy(() => clearInterval(scheduler));
 
	

</script>
	<nav class="navbar navbar-expand-md navbar-dark bg-dark">
		<a class="navbar-brand" href="#">Crypto App</a>
        <ul class="navbar-nav w-100">
            <li class="nav-item"><a href="#" class="nav-link">Home</a></li>
            <li class="nav-item"><a href="#" class="nav-link">Link</a></li>
            <!--<li class="nav-item ml-md-auto"><a href="#" class="btn btn-primary switch">Switch Light/Dark</a></li>-->
        </ul>
	</nav>
	<section class="container-fluid">
		{JSON.stringify(pancake_lp)}		
		
	
	<div class="row">
		<div class="col-md-4">
			<h2>Binance Info</h2>
			<table class="table table-dark">
				<th>Symbol</th>
				<th>Amount</th>
				<th>USD Value of Token</th>
				<th>USD Value Held</th>
					{#if binance_assets != null}
						{#each binance_assets as k}
						<tr>
							<td>{k.asset}</td>
							<td>{k.free}</td>
							<td>${k.current_price.toFixed(2)}</td>
							<td>${k.amount_in_usd.toFixed(2)}</td>
						</tr>
						{/each}
					{:else}
						<tr>
							<td>Loading...</td>
						</tr>
					{/if}
			</table>
		</div>
		<div class="col-md-3">
			<div class="card text-white bg-primary mb-3" style="max-width: 18rem;">
				<div class="card-header">Pancake Swap LP</div>
				<div class="card-body">
				{#if pancake_lp != null}
					<div class="row">
						<div class="col-md-6 text-center">
							<h5 class="card-title">Deposited</h5>
							<p class="card-text">${pancake_lp.deposited_money.toFixed(2)}</p>
						</div>
						<div class="col-md-6 text-center">
							<h5 class="card-title">Yielded</h5>
							<p class="card-text">${pancake_lp.yield_money.toFixed(2)}</p>
						</div>
					</div>
					<div class="row">
						<div class="col-md-12 text-center">
							<h5 class="card-title">Total</h5>
							<p class="card-text">${pancake_lp.total_money.toFixed(2)}</p>
						</div>
				</div>
				  {#each pancake_lp.vaultStats as p}
				  <div class="card text-white bg-dark mb-3" style="max-width: 18rem;">
				  	<div class="card-header">{p.poolName}</div>
					<div class="card-body">
						<p class="card-text">{p.token0} count: {p.currentToken0Count.toFixed(6)}</p>
						<p class="card-text">Change in count:  {(((p.currentToken0Count - p.depositToken0Count) / p.depositToken0Count)*100).toFixed(2)}%</p>
						<p class="card-text">{p.token1} count: {p.currentToken1Count}</p>
						<p class="card-text">Change in count:  {(((p.currentToken1Count - p.depositToken1Count) / p.depositToken1Count)*100).toFixed(2)}%</p>
						
					</div>
				</div>
				  {/each}
				{:else}
					<p>Loading...</p>
				{/if}
				</div>
			  </div>
		</div>
	</div>
	<p></p>
</section>

