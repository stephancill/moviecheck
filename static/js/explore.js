$(document).ready(function() {
	let params = (new URL(document.location)).searchParams
	
	$("#search-input").val(params.get("query") || "")
})