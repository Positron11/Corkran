// Make the main page invisible before it is done loading
document.getElementById('main').style.opacity = "0";


// Show overlay if page takes more than 5 milliseconds to load
var showTimeout = setTimeout(function() {
	document.getElementById('loading-overlay').style.opacity = "1";
}, 5);


// Hide overlay when page finished loading
jQuery(window).on("load", function() {
	clearTimeout(showTimeout);


	// hide the overlay
	document.getElementById('loading-overlay').style.opacity = "0";


	// show the main page
	document.getElementById('main').style.opacity = "1";


	// remove the overlay after it's done hiding
	setTimeout(function() {
		$("#loading-overlay").remove();
	}, 500);


	// fade out and remove alert
	setTimeout(function() {
		if ($(".alert").length) {
			$(".alert").fadeOut( "slow", function() {
				$(this).remove();
			});
		}
	}, 10000);
});


// Main
$(function() {
	
	// Initialize page
	floatMessage();
	resizeSidebar();
	vertically_truncate();
	calculateProgressBar();
	fadeTruncateArticles();

	// Initialize autosize
	autosize($('textarea'));
	autosize.update($("textarea"));


	// Toggle mobile navbar links
	$(document).on('click', '.menu-btn', function(e) {
		e.preventDefault();
		$(".navbar").toggleClass("mobile-show");
	});


	// Toggle comment reply box
	$(document).on('click', '.toggle-btn.reply', function(e) {
		e.preventDefault();
		toggleCommentEditor("reply", $(this));
	});

	// Toggle comment edit box
	$(document).on('click', '.toggle-btn.edit', function(e) {
		e.preventDefault();
		toggleCommentEditor("edit", $(this));
	});


	// On scroll...
	$(window).on("scroll", function() {
		floatMessage();
		calculateProgressBar();
	});

	// On resize...
	$(window).on("resize", function() {
		resizeSidebar();
		fadeTruncateArticles();
	});


	// Prevent empty textarea
	$("textarea").each(function() {
		$(this).on("keydown", function(e) {
			var c = $(this).val().length;

			// prevent directly typing leading spaces or newlines
			if (c === 0)
				return (e.which !== "13" && e.which !== 32);

			// disable submit button if empty
			$(this).parent().find("button").prop("disabled", ($.trim($(this).val()) === ""));
		});
	});

	// Automatically resize textarea
	$("textarea").on('input', function() {
		autosize.update($("textarea"));
	});


	// replace all other separators with spaces
	$("#suggested_tags").on('input', function() {
		$(".suggestions-input").val($(".suggestions-input").val().replace(/[\s,]+/g, " "));
	});

	// New suggestion engine for tags
	suggestionsEngine($("#id_tags"), $("#suggested_tags"), $("#suggested_tags .tag"));

	// Show uploaded file in file input label
	$('input[type="file"]').change(function(e) {
		var fileName = e.target.files[0].name;
		var label = $("label[id='" + $(this).attr('id') + "_label']");
		label.children("span").text(fileName);
	});

	// store original attribution value
	var value = $("#id_attribution").prop("value");
	
	// Disable thumbnail upload button and attribution if remove thumbnail checked
	$('#thumbnail-clear_id').click(function() {
		if ($(this).prop("checked") === true) {
			$("#thumbnail_button, #id_attribution").addClass("disabled");
			$("#id_attribution")
			.prop("placeholder", "No image, no attribution...")
			.prop("value", "");
		} else {
			$("#thumbnail_button, #id_attribution").removeClass("disabled");
			$("#id_attribution")
			.prop("placeholder", "Attribution or caption...")
			.prop("value", value);
		}
	});

	// Unsplash image search
	$("#unsplash_search_form").submit(function(e) {
		// prevent reload on image search
		e.preventDefault();
		// get query and encode
		var query = encodeURIComponent(document.getElementById("unsplash_search").value);
		// search if query or go to unsplash home page
		if (query) {
			window.open("https://unsplash.com/s/photos/" + String(query), '_blank');
		} else {
			window.open("https://unsplash.com/", '_blank');
		}
	});
});


// CALCULATE PROGRESS BAR
function calculateProgressBar() {
	// if on article detail page...
	if ($(".main-article").length) {
		var y_offset, height, completed;
		var bottom_height = $(document).height() - $(".main-article .content").outerHeight() - 127;

		// if the article is substantially larger than page
		if (bottom_height > $(window).height()) {
			height = $(".main-article .content").outerHeight();
			y_offset = -($(".main-article .content").offset().top - $(window).scrollTop() - 127);
			completed = y_offset / height * 100;
		} else {
			y_offset = window.pageYOffset;
			height = $(document).height() - $(window).height();
			completed = y_offset / height * 100;
		}

		// update progress bar width
		$(".progress-bar").css("width", completed + "%");

		// show scroll to top button if started reading article
		if (completed <= 1) {
			scrollTopButton("hide");
		} else {
			scrollTopButton("show");
		}
	}
}


// SHOW OR HIDE SCROLL TOP BUTTON
function scrollTopButton(state) {
	if (state == "show") {
		$(".scroll-top-btn").css("opacity", "1");
		$(".scroll-top-btn").css("transform", "scale(1)");
	} else {
		$(".scroll-top-btn").css("opacity", "0");
		$(".scroll-top-btn").css("transform", "scale(0)");
	}
}


// SCROLL TO TOP
function scrollToTop() {
	const c = document.documentElement.scrollTop || document.body.scrollTop;
	if (c > 0) {
		window.requestAnimationFrame(scrollToTop);
		window.scrollTo(0, c - c / 8);
	}
}


// TRUNCATE ANNOUNCEMENT IN SIDEBAR
function resizeSidebar() {
	// approximate fixed value for distance from top of sidebar to bottom of page
	var height = window.innerHeight - 200;

	// set sidebar height
	$('.sidebar').css("height", height);
}


// TOGGLE COMMENT EDITORS
function toggleCommentEditor(editor, button) {
	var type, text, other, other_text;
	
	if (editor == "reply") {
		type = ".reply";
		text = "Reply";
		other = ".edit";
		other_text = "Edit";
	} else {
		type = ".edit";
		text = "Edit";
		other = ".reply";
		other_text = "Reply";
	}

	// close all other editors of same type
	$(".comments")
		.find(".comment")
		.not(button.closest(".comment"))
		.find(".editor" + type).hide().end()
		.find(".toggle-btn" + type).text(text);

	// close all editors of other type
	$(".comments")
		.find(".comment")
		.find(".editor" + other).hide().end()
		.find(".toggle-btn" + other).text(other_text);

	// if edit button, show all other comment contents
	if (editor == "edit") {
		$(".comments")
			.find(".comment")
			.not(button.closest(".comment"))
			.find($(".content")).show();
	}

	// if reply button, reset all comment contents
	if (editor == "reply") {
		$(".comments .comment .content").show();
	}

	// hide other buttons in same button box
	button.closest(".comment-btn-container").find(".button").not(button).toggle();

	// show all other buttons in other button boxes
	$(".comments")
		.find(".comment")
		.not(button.closest(".comment"))
		.find($(".comment-btn-container .button")).show();

	// toggle textbox and button text
	button
		.text((button.text() == text ? 'Close Editor' : text)) // toggle text
		.closest(".comment").find(".editor" + type).toggle(); // toggle textbox

	// if edit button, toggle comment
	if (editor == "edit") {
		button.closest(".comment").find(".content").toggle();
	}

	// resize editor textarea to fit comment
	autosize.update($("textarea"));
}

// FADE TRUNATE ARTICLES
function fadeTruncateArticles() {
	$(".article-preview").each(function() {
		// If text overflows and is not already truncated
		if (this.offsetHeight < this.scrollHeight && !$(this).find(".fade").length) {
			$(this).append("<div class='fade'></div>");
		}
	});
}

// FLOAT MESSAGE BASED ON SCROLL POSITION
function floatMessage() {
	if ($(".alert").length) {
		if (($(".alert").offset().top - (window.pageYOffset + $(".navbar").outerHeight())) <= 10) {
			$(".alert").addClass("floating");
		} else {
			$(".alert").removeClass("floating");
		}
	}
}

// SUGGESTION ENGINE
function suggestionsEngine(input, container, suggestion) {
	// Show tag suggestions
	input.on('input', function() {

		// split sentence by possible delimiters
		var words = input.val().toLowerCase().split(/[\s,]+/);

		// get last word
		var word = words.pop();

		// if not empty and currently typing a word, get suggestions
		if (word) {
			// show main block
			container.show();

			// show matching tags
			suggestion.each(function() {
				// get tag text as lowercase
				var text = $(this).text().toLowerCase();

				// if tag matches input and tag doesn't already exist
				if (text.includes(word) && $.inArray(text, words) < 0) {
					// show tag in suggestions
					$(this).show();
				} else {
					// remove tag from suggestions
					$(this).hide();
				}
			});
		} else {
			// hide entire block
			container.hide();
		}

		// if no suggestions, hide entire block
		if (!suggestion.is(":visible")) {
			container.hide();
		}
	});

	// Put clicked tag in textbox
	suggestion.on("click", function() {
		// get all words in input
		var words = input.val().split(/[\s,]+/);

		// remove unfinished tag from words list
		words.pop();

		// add tag to end of words list
		words.push($(this).text());

		// replace input box value with current tags 
		input.val(words.join(" ") + " ");

		// focus and move to end of input
		input.each(function() {
			$(this).focus();
			if (this.setSelectionRange) {
				var len = $(this).val().length * 2;
				this.setSelectionRange(len, len);
			} else {
				$(this).val($(this).val());
			}
		});

		// Hide suggestions
		container.hide();
	});
}