// autoComplete.js on typing event emitter
document.querySelector("#search-input").addEventListener("autoComplete", event => {
	console.log(event);
});
// The autoComplete.js Engine instance creator
const autoCompletejs = new autoComplete({
	data: {
		src: async () => {
			// Loading placeholder text
			document
				.querySelector("#autoComplete")
				.setAttribute("placeholder", "Loading...");
			// Fetch External Data Source
			const source = await fetch(`/explore/search?query=${query}`);
			const data = await source.json();
			// Post loading placeholder text
			document
				.querySelector("#autoComplete")
				.setAttribute("placeholder", "Food & Drinks");
			// Returns Fetched data
			return data;
		},
		key: ["food", "cities", "animals"],
		cache: false
	},
	sort: (a, b) => {
		if (a.match < b.match) return -1;
		if (a.match > b.match) return 1;
		return 0;
	},
	placeHolder: "Food & Drinks",
	selector: "#autoComplete",
	threshold: 0,
	debounce: 0,
	searchEngine: "strict",
	highlight: true,
	maxResults: 5,
	resultsList: {
		render: true,
		container: source => {
      source.setAttribute("id", "autoComplete_list");
		},
		destination: document.querySelector("#autoComplete"),
		position: "afterend",
		element: "ul"
	},
	resultItem: {
		content: (data, source) => {
      source.innerHTML = data.match;
		},
		element: "li"
	},
	noResults: () => {
		const result = document.createElement("li");
		result.setAttribute("class", "no_result");
		result.setAttribute("tabindex", "1");
		result.innerHTML = "No Results";
		document.querySelector("#autoComplete_list").appendChild(result);
	},
	onSelection: feedback => {
		const selection = feedback.selection.value.food;
		// Render selected choice to selection div
		document.querySelector(".selection").innerHTML = selection;
		// Clear Input
		document.querySelector("#autoComplete").value = "";
		// Change placeholder with the selected value
		document
			.querySelector("#autoComplete")
			.setAttribute("placeholder", selection);
		// Concole log autoComplete data feedback
		console.log(feedback);
	}
});

// Toggle Search Engine Type/Mode
document.querySelector(".toggeler").addEventListener("click", function() {
  // Holdes the toggle buttin alignment
  const toggele = document.querySelector(".toggele").style.justifyContent;

  if (toggele === "flex-start" || toggele === "") {
    // Set Search Engine mode to Loose
    document.querySelector(".toggele").style.justifyContent = "flex-end";
    document.querySelector(".toggeler").innerHTML = "Loose";
    autoCompletejs.searchEngine = "loose";
  } else {
    // Set Search Engine mode to Strict
    document.querySelector(".toggele").style.justifyContent = "flex-start";
    document.querySelector(".toggeler").innerHTML = "Strict";
    autoCompletejs.searchEngine = "strict";
  }
});