$(document).ready(function() {
    $(".movie form").on("submit", function (e) {
        let form = $(this)
        e.preventDefault();
        const data = new FormData(form[0]);
        fetch(form.attr("action"), {
            method: form.attr("method"),
            body: data
        }).then(function(response) {
            if (response.status >= 200 && response.status < 300) {
                location.reload()
            }
        })
    })

    $(".history-container tr .reload-on-submit").on("submit", function (e) {
        let form = $(this)
        e.preventDefault();
        const data = new FormData(form[0]);
        fetch(form.attr("action"), {
            method: form.attr("method"),
            body: data
        }).then(function(response) {
            if (response.status >= 200 && response.status < 300) {
                location.reload()
            }
        })
    })

    $(".history-container tr .rating-form input").change(function (e) {
        let button = $(this)
        let form = button.parents("form")
        const data = new FormData(form[0]);
        fetch(form.attr("action"), {
            method: form.attr("method"),
            body: data
        })
    })

    $(".history-container .date button").click(function (e) {
        $(".date-container form").hide()
        $(".date").show()
        let button = $(this)
        button.parents(".date").hide()
        button.parents(".date").siblings("form").show()
    })
})