// Get loading overlay and main container elements
var main_container = document.getElementById('main');
var loading_overlay = document.getElementById('loading-overlay');


// Make the main page invisible before it is done loading
main_container.style.opacity = "0";


// Show overlay if page takes more than 5 milliseconds to load
var showTimeout = setTimeout(function () {
	loading_overlay.style.display = "flex";
	loading_overlay.style.opacity = "1";
}, 5);


// Hide overlay when page finished loading
$(window).on("load", function () {
	clearTimeout(showTimeout);

	// hide the overlay
	loading_overlay.style.opacity = "0";

	// show the main page
	main_container.style.opacity = "1";

	// remove the overlay after it's done hiding
	setTimeout(function () {
		loading_overlay.remove();
	}, 500);

	// fade out and remove alert after 10 seconds
	$(".alert").each(function () {
		autoRemoveAlert(this);
	});
});


// Main
$(function () {
	// Initialize page
	styleNavbar();
	floatMessage();
	resizeSidebar();
	scrollTopButton();
	fadeTruncateArticles();

	// Initialize vertical truncator plugin
	vertically_truncate();

	// Initialize autosize
	autosize($('textarea'));
	autosize.update($("textarea"));

	// initialize are-you-sure form close manager plugin
	$('form.confirm-leave').areYouSure();


	// Smooth scrolling
	$(document).on('click', 'a[href^="#"]', function (e) {
		e.preventDefault();
		$('html, body').stop().animate({
			scrollTop: $($(this).attr('href')).offset().top
		}, 1000, 'easeOutQuint');
	});


	// Disable alert-offset class if no alert
	if (!$(".alert").length) {
		$(".offset-alert").removeClass("offset-alert");
	}

	// Close alert on clicking close button
	$(document).on('click', '.alert.floating .close-btn', function (e) {
		$(this).parent(".alert").hide("fast", function () {
			$(this).remove();
		});
	});


	// Toggle mobile navbar links
	$(document).on('click', '#nav_menu_btn', function (e) {
		e.preventDefault();
		$(".navbar").toggleClass("mobile-show");
	});

	// Hide mobile navbar links if clicked outside navbar
	$(document).on('click', 'body', function (e) {
		if ((!e.target.id == "navbar" || !$(e.target).closest('#navbar').length) && $(".navbar").hasClass("mobile-show")) {
			$(".navbar").removeClass("mobile-show");
		}
	});


	// toggle dropdown
	$(document).on('click', '.dropdown-label', function (e) {
		e.preventDefault();
		$(this).parent(".dropdown").toggleClass("dropped");
	});

	// Hide mobile dropdowns if clicked outside dropdown
	$(document).on('click', 'body', function (e) {
		if (!$(e.target).closest('.dropdown').length && $(".dropdown").hasClass("dropped")) {
			$(".dropdown").removeClass("dropped");
		}
	});


	// Toggle comment reply box
	$(document).on('click', '.toggle-btn.reply', function (e) {
		e.preventDefault();
		toggleCommentEditor("reply", $(this));
	});

	// Toggle comment edit box
	$(document).on('click', '.toggle-btn.edit', function (e) {
		e.preventDefault();
		toggleCommentEditor("edit", $(this));
	});


	// On scroll...
	$(window).on("scroll", function () {
		styleNavbar();
		floatMessage();
		scrollTopButton();
	});

	// On resize...
	$(window).on("resize", function () {
		resizeSidebar();
		fadeTruncateArticles();
		$('.list-box.nowrap').each(function () {
			blurListBox(this);
		});
	});


	// Prevent empty textarea
	$("textarea").each(function () {
		$(this)
			// prevent leading newlines or spaces
			.on("keydown", function (e) {
				// get pressed key
				var c = $(this).val().length;
				// prevent directly typing leading spaces or newlines if textbox empty
				if (c === 0) {
					return (e.which !== "13" && e.which !== 32);
				}
			})
			// prevent empty textarea from middle
			.on("input", function () {
				// disable submit button if empty
				$(this).parent().find("button").prop("disabled", ($.trim($(this).val()) === ""));
			});
	});

	// Automatically resize textarea
	$("textarea").on('input', function () {
		autosize.update($("textarea"));
	});


	// BLUR SIDES OF NOWRAP LISTBOXES
	$('.list-box.nowrap').each(function () {
		// initialize blur
		blurListBox(this);

		// calculate blur on scroll
		$(this).scroll(function () {
			blurListBox(this);
		});
	});


	// New suggestion engine for tags
	suggestionsEngine($("#id_tags"), $("#suggested_tags"), $("#suggested_tags .tag"));

	// replace all other separators with spaces
	$("#id_tags").on('input', function () {
		// get keypress code
		$("#id_tags").on('keydown', function () {
			tags_input_keypress = event.which || event.keyCode || event.charCode;
		});

		// if keypress is not backspace or delete
		if (tags_input_keypress != 8 && tags_input_keypress != 46) {
			$("#id_tags").val($("#id_tags").val().replace(/[\s,]+/g, ", "));
		}
	});

	// Show uploaded file in file input label
	$('input[type="file"]').change(function (e) {
		var fileName = e.target.files[0].name;
		var label = $("label[id='" + $(this).attr('id') + "_label']");
		label.children("span").text(fileName);
	});

	// store original attribution value
	var value = $("#id_attribution").prop("value");

	// Disable thumbnail upload button and attribution if remove thumbnail checked
	$('#thumbnail-clear_id').click(function () {
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
	$("#unsplash_search_form").submit(function (e) {
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


// STYLE NAVBAR
function styleNavbar() {
	calculateProgressBar();
	$(".navbar").css("box-shadow", window.pageYOffset > 0 ? "0 5px 3px -3px rgba(0,0,0,0.1)" : "none");
}


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
	}
}


// SHOW OR HIDE SCROLL TOP BUTTON
function scrollTopButton() {
	var state;

	// if on article detail page and started reading article...
	if ($(".main-article").length && parseFloat($(".progress-bar").css("width")) >= 1) {
		state = "show";
	// otherwise if not on detail page and at least scrolled down a bit...
	} else if (!$(".main-article").length && window.pageYOffset >= 100) {
		state = "show";
	// otherwise just hide
 	} else {
		state = "hide";
	}

	// edit button css based on state
	$(".scroll-top-btn").css("opacity", state == "show" ? 1 : 0);
	$(".scroll-top-btn").css("pointer-events", state == "show" ? "all" : "none");
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

	// set values
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
	$(".article-preview").each(function () {
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
	input.on('input', function () {

		// split sentence by possible delimiters
		var words = input.val().toLowerCase().split(/[\s,]+/);

		// get last word
		var word = words.pop();

		// if not empty and currently typing a word, get suggestions
		if (word) {
			// show main block
			container.show();

			// show matching tags
			suggestion.each(function () {
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
	suggestion.on("click", function () {
		// get all words in input
		var words = input.val().split(/[\s,]+/);

		// remove unfinished tag from words list
		words.pop();

		// add tag to end of words list
		words.push($(this).text());

		// replace input box value with current tags 
		input.val(words.join(", ") + " ");

		// focus and move to end of input
		input.each(function () {
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


// FADE OUT AND REMOVE ALERT AFTER 10 SECONDS
function autoRemoveAlert(page_alert) {
	setTimeout(function () {
		// fade out alert
		$(page_alert).fadeOut("slow", function () {
			// remove alert from DOM after fading out
			$(this).remove();
		});
	}, 10000);
}


// BLUR RIGHT AND LEFT SIDES OF NOWRAP LISTBOX
function blurListBox(listbox) {
	// handle left blur
	if (listbox.scrollLeft > 0) {
		$(listbox).addClass("blur-left");
	} else {
		$(listbox).removeClass("blur-left");
	};

	// get total width of children in listbox
	var content_width = 0;
	$(listbox).find("> *").each(function () {
		content_width += ($(this).outerWidth(true));
	});

	// handle right blur
	if ((content_width - 5) - listbox.scrollLeft > $(listbox).width()) {
		$(listbox).addClass("blur-right");
	} else {
		$(listbox).removeClass("blur-right");
	};
}


// TOGGLE ARTICLE ZEN MODE VIEW
function toggleZenMode() {
	if (!$(".zen-mode").hasClass("visible")) {
		// remove body scrollbar and compensate width with padding to avoid jerk
		$("body")
			.css("overflow", "hidden")
			.css("padding-right", getScrollbarWidth() + "px");
		
		// make zen mode overlay visible
		$(".zen-mode").addClass("visible");
	} else {
		// remove zen mode overlay
		$(".zen-mode").removeClass("visible");

		// wait for overlay to go, then add body scrollbar
		$(".zen-mode").on("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function() {
			if (!$(".zen-mode").hasClass("visible")) {
				$("body")
					.css("overflow", "auto")
					.css("padding-right", "0px");
			}
		});
	}
}


// GET SCROLLBAR WIDTH
function getScrollbarWidth() {
	// Creating invisible container
	const outer = document.createElement('div');
	outer.style.visibility = 'hidden';
	outer.style.overflow = 'scroll'; // forcing scrollbar to appear
	outer.style.msOverflowStyle = 'scrollbar'; // needed for WinJS apps
	document.body.appendChild(outer);

	// Creating inner element and placing it in the container
	const inner = document.createElement('div');
	outer.appendChild(inner);

	// Calculating difference between container's full width and the child width
	const scrollbarWidth = (outer.offsetWidth - inner.offsetWidth);

	// Removing temporary elements from the DOM
	outer.parentNode.removeChild(outer);

	return scrollbarWidth;
}