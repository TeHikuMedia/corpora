function nextPageTransition(currPage, nextPage) {
	currPage.addClass("pt-page-moveToLeft pt-page-fadeOut");
	nextPage.addClass("pt-page-current pt-page-moveFromRight");

	nextPage.find(".button").show();

	currPage.on("transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd",   
		function(event) {
			if (event.target.id == currPage.attr('id')) {
				nextPage.removeClass("pt-page-moveFromRight");
				currPage.removeClass("pt-page-current pt-page-moveToLeft pt-page-fadeOut");

				currPage.find(".button").hide();
			};
	});
}

function prevPageTransition(currPage, prevPage) {
	currPage.addClass("pt-page-moveToRight pt-page-fadeOut");
	prevPage.addClass("pt-page-current pt-page-moveFromLeft");

	prevPage.find(".button").show();
	
	currPage.on("transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd",
		function(event) {
			if (event.target.id == currPage.attr('id')) {
				prevPage.removeClass("pt-page-moveFromLeft");
				currPage.removeClass("pt-page-current pt-page-moveToRight pt-page-fadeOut");

				currPage.find(".button").hide();
			};
	});
}