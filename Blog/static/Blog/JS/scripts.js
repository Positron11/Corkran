// Get loading overlay and main container elements
var main_container = document.getElementById('main');
var loading_overlay = document.getElementById('loading_overlay');


// Make the main page invisible before it is done loading
main_container.style.opacity = "0";


// Show overlay if page takes more than 5 milliseconds to load
var showTimeout = setTimeout(function () {
	loading_overlay.style.display = "flex";
	loading_overlay.style.opacity = "1";
}, 5);


// Add alert-offset class if alert
if ($(".alert").length && $(".anchor").length) {
	$(".anchor").addClass("offset-alert");
}


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
	setTimeout(function () {
		// fade out alert
		$(".alert").fadeOut("slow", function () {
			// remove alert from DOM after fading out
			$(this).remove();
			// disable alert-offset class
			if ($(".anchor").length) {
				$(".anchor").removeClass("offset-alert");
			}
		});
	}, 10000);
});


// Set global variables
var reading_progress = 0;


// Main
$(function () {
	// Initialize page
	styleNavbar();
	floatMessage();
	resizeSidebar();
	fadeTruncateArticles();
	calculateProgressBar();
	scrollTopButton();

	// Set sidebar
	if ($(".main-article").length) {
		switchSidebar(reading_progress > 0 && reading_progress < 100 ? "article_detail" : "default");
	}

	// Initialize vertical truncator plugin
	vertically_truncate();

	// Initialize autosize
	autosize($('textarea'));
	autosize.update($("textarea"));

	// Initialize are-you-sure form close manager plugin
	$('form.confirm-leave').areYouSure();


	// Smooth scrolling
	$(document).on('click', 'a[href^="#"]', function (e) {
		e.preventDefault();
		$('html, body').stop().animate({
			scrollTop: $($(this).attr('href')).offset().top
		}, 1000, 'easeOutQuint');
	});


	// On scroll...
	$(window).on("scroll", function () {
		styleNavbar();
		floatMessage();
		calculateProgressBar();
		scrollTopButton();

		// Set sidebar
		if ($(".main-article").length) {
			switchSidebar(reading_progress > 0 && reading_progress < 100 ? "article_detail" : "default");
		}
	});

	// On resize...
	$(window).on("resize", function () {
		resizeSidebar();
		fadeTruncateArticles();

		// blur overflow boxes
		$(".blur-overflow").each(function () {
			blurOverflowBox(this);
		});

		// reposition dropped dropdown
		if ($(".dropdown.dropped .dropdown-label").length) {
			positionDropdown($(".dropdown.dropped .dropdown-label")[0]);
		}
	});


	// When clicking alert...
	$(document).on('click', '.alert', function (e) {
		// close alert on clicking close button
		if ($(e.target).hasClass("close-btn")) {
			$(this).hide("fast", function () {
				// remove from DOM
				$(this).remove();
				// disable alert-offset class
				if ($(".anchor").length) {
					$(".anchor").removeClass("offset-alert");
				}
			});
		// expand or contract message
		} else {
			$(this).find(".message").toggleClass("single-line-text");
		}
	});


	// Toggle mobile navbar links
	$(document).on('click', '#nav_menu_btn', function (e) {
		e.preventDefault();
		$("#navbar").toggleClass("mobile-show");
	});

	// Hide mobile navbar links if clicked outside navbar
	$(document).on('click', 'body', function (e) {
		if ((!e.target.id == "navbar" || !$(e.target).closest('#navbar').length) && $("#navbar").hasClass("mobile-show")) {
			$("#navbar").removeClass("mobile-show");
		}
	});


	// If mobile
	if (window.matchMedia("(pointer:coarse)").matches) {
		// toggle dropdown
		$(document).on('click', '.dropdown-label', function (e) {
			e.preventDefault();
			$(this).parent(".dropdown").toggleClass("dropped");
		});
		
		// hide mobile dropdowns if clicked outside dropdown
		$(document).on('mousedown', 'body', function (e) {
			currently_dropped = $(".dropdown.dropped");
			if ($(currently_dropped).length) {
				if (!$(e.target).closest(currently_dropped).length) {
					$(currently_dropped).removeClass("dropped");
				}
			}
		});
	}

	// Position dropdown
	$(document).on('click mouseenter', '.dropdown-label', function (e) {
		e.preventDefault();
		positionDropdown(this);
	});


	// Search suggestions
	$(document).on('input', '#article_search_input', function (e) {
		if ($(this).val().length > 0) {
			$("#search_suggestions").addClass("visible");
			
			if ($(".search-suggestion-group").is(":visible")) {
				$("#no_suggestions").hide();
			} else {
				$("#no_suggestions").show();
			}
		} else {
			$("#search_suggestions").removeClass("visible");
		}
	});

	// Hide suggestion box if clicked outside or on suggestion
	$(document).on('click', 'body', function (e) {
		if ((!$(e.target).closest('#search_suggestions').length && $("#search_suggestions").hasClass("visible")) || $(e.target).closest('.search-suggestion').length) {
			$("#search_suggestions").removeClass("visible");
		} 
	});

	// New suggestion engine for each category
	$("#search_suggestions .search-suggestion-group").each(function (e) {
		suggestionsEngine($("#article_search_input"), $(this), $(this).find(" .search-suggestion"), "full");
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

	// Toggle comment linker text
	$(document).on('click', '.direct-linker', function() {
		var button = $(this);
		var orig_text = $(this).text()
		button.text("Link copied");
		setTimeout(function () {
			button.text(orig_text);
		}, 3000);
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

	
	// Blur overflow blur box
	$('.blur-overflow').each(function () {
		// initialize blur
		blurOverflowBox(this);

		// calculate blur on scroll
		$(this).scroll(function () {
			blurOverflowBox(this);
		});
	});

	// Click to scroll horizontal listbox
	$(document).on('click', '.list-box.blur-overflow', function (e) {
		var scroll_pos = $(this).scrollLeft();
		var bounding_box = this.getBoundingClientRect();
		
		// scroll right
		if (e.pageX > bounding_box.right - 60 && $(this).hasClass("blur-right")) {
			$(this).stop().animate({
				scrollLeft: scroll_pos + 200
			}, 1000, 'easeOutQuint');
			
			// scroll left
		} else if (e.pageX < bounding_box.left + 60 && $(this).hasClass("blur-left")) {
			$(this).stop().animate({
				scrollLeft: scroll_pos - 200
			}, 1000, 'easeOutQuint');
		}
	});

	// Click to scroll vertical blur box
	$(document).on('click', '.blur-overflow.vertical', function (e) {
		var scroll_pos = $(this).scrollTop();
		var bounding_box = this.getBoundingClientRect();
		
		// scroll up
		if (e.clientY < bounding_box.top + 60 && $(this).hasClass("blur-top")) {
			$(this).stop().animate({
				scrollTop: scroll_pos - 200
			}, 1000, 'easeOutQuint');
		}

		// scroll down
		if (e.clientY > bounding_box.bottom - 60 && $(this).hasClass("blur-bottom")) {
			$(this).stop().animate({
				scrollTop: scroll_pos + 200
			}, 1000, 'easeOutQuint');
		}
	});


	// Pre-select currently used category group
	categorySelect($(".category-select:checked").first()[0]);

	// Disable other categories when one selected
	$(document).on('change', '.category-select', function (e) {
		categorySelect(this);
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

	// Put clicked tag in textbox
	$("#suggested_tags .tag").on("click", function () {
		// get all words in input
		var words = $("#id_tags").val().split(/[\s,]+/);

		// remove unfinished tag from words list
		words.pop();

		// add tag to end of words list
		words.push($(this).text());

		// replace input box value with current tags 
		$("#id_tags").val(words.join(", ") + " ");

		// focus and move to end of input
		$("#id_tags").each(function () {
			$(this).focus();
			if (this.setSelectionRange) {
				var len = $(this).val().length * 2;
				this.setSelectionRange(len, len);
			} else {
				$(this).val($(this).val());
			}
		});

		// Hide suggestions
		$("#suggested_tags").hide();
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


	// Mail filter
	if ($(".mail").length) {
		$(document).on('click', '#mail_filter > *', function () {
			// clear filters 
			$('#clear_mail_filters').click(function () {
				$("#mail_filter input").prop("checked", false);
			});

			// sort if any filters applied
			if($("#mail_filter input").is(':checked')) {
				// hide all mail
				$(".mail").hide();

				// show all relevant mail
				$(":checkbox:checked").each(function () {
					$(".mail." + $(this).attr("id") + "_mail").show();
				});

			// otherwise show all mail
			} else {
				$(".mail").show();
			}

			// if no mail visible show empty filter card
			if (!$(".mail").is(":visible")) {
				$("#empty_filtered_mail").show();
			} else {
				$("#empty_filtered_mail").hide();
			}

			// keep mail filter bar at top
			$('html, body').scrollTop($("#mail_filter_anchor").offset().top);
		});
	}
});


// STYLE NAVBAR
function styleNavbar() {
	if (window.pageYOffset > 0) {
		$("#navbar").addClass("floating");
	} else {
		$("#navbar").removeClass("floating");
	}
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

		// update progress bar width and data
		$(".reading-progress-bar")
			.css("width", completed + "%")
			.attr("data-progress", Math.max(0, Math.min(parseInt(completed), 100)) + "%");

		// show progress percentage badge if reading
		if (completed > 0 && completed < 100) {
			$(".reading-progress-bar").addClass("show-progress");
		} else {
			$(".reading-progress-bar").removeClass("show-progress");
		}

		// update global reading progress var
		reading_progress = completed;
	}
}


// SHOW OR HIDE SCROLL TOP BUTTON
function scrollTopButton() {
	var state;

	// if on article detail page and started reading article...
	if ($(".main-article").length && reading_progress > 1) {
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
	var sidebar_height = window.innerHeight - parseFloat($("#sidebar").css("top"));
	var sidebar_content_height = sidebar_height - $("#sidebar").find(".header").outerHeight(true) - 40;

	// set sidebar height
	$('#sidebar').css("max-height", sidebar_height);
	$('#sidebar .content').css("max-height", sidebar_content_height);
}

// SWITCH SIDEBARS
function switchSidebar(sidebar) {
	// show selected sidebar's elements
	$("[data-sidebar]").hide();
	$("[data-sidebar='" + sidebar + "']").show();
	
	// resize sidebar to account for possible changed header size
	resizeSidebar();
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
		if (this.offsetHeight < this.scrollHeight && !$(this).find(".fade-bottom-overlay").length) {
			$(this).append("<div class='fade'></div>");
		}
	});
}


// FLOAT MESSAGE BASED ON SCROLL POSITION
function floatMessage() {
	if ($(".alert").length) {
		if ($(".alert").offset().top == window.pageYOffset + parseFloat($(".alert").css("top"))) {
			$(".alert").addClass("floating");
		} else {
			$(".alert").removeClass("floating");
		}
	}
}


// SUGGESTION ENGINE
function suggestionsEngine(input, container, suggestion, mode) {
	// Show tag suggestions
	input.on('input', function () {
		// raw input
		var raw_input = input.val().toLowerCase().trim();

		// split raw input by possible delimiters
		var words = raw_input.split(/[\s,]+/);

		// get last word
		var word = words[words.length - 1];

		// check if input, or typing word
		var search_signal = mode == "full" ? raw_input : word;
		
		// if not empty and currently typing a word, get suggestions
		if (search_signal) {
			// show main block
			container.show();

			// show matching suggestions
			suggestion.each(function () {
				// get suggestion text as lowercase
				var text = $(this).text().toLowerCase();

				// Check mode
				var forward_search_segment = mode == "full" ? containsAny(text, words) : text.includes(word);
				var backward_search_segment = mode == "full" ? raw_input.includes(text) : word.includes(text);
				var preserve_options = mode == "full" ? true : $.inArray(text, words) < 0;

				// if suggestion matches input
				if ((forward_search_segment || backward_search_segment) && preserve_options) {
					// prioritize results
					if (mode == "full") {
						$(this).css("order", $(suggestion).length - containsAny(text, words));
					}
					// show suggestion
					$(this).show();
				} else {
					// hide suggestion
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
}


// CHECK IF STRING CONTAINS TEXT FROM ARRAY
function containsAny(text, array) {
	var matches = 0;
	for (substring in array) {
		if (text.includes(array[substring])) {
			matches++;
		}
	}
	return matches;
}


// BLUR OVERFLOW BOX
function blurOverflowBox(overflow_box) {
	// get blur class
	var blur_class = $(overflow_box).hasClass("vertical") ? "blur-top" : "blur-left";
	
	// handle left/top blur
	if ($(overflow_box).hasClass("vertical") && overflow_box.scrollTop > 0 || $(overflow_box).hasClass("horizontal") && overflow_box.scrollLeft > 0) {
		$(overflow_box).addClass(blur_class);
	} else {
		$(overflow_box).removeClass(blur_class);
	};

	// get total width of children in overflow_box
	var content_size = $(overflow_box).hasClass("vertical") ? overflow_box.scrollHeight : overflow_box.scrollWidth;

	// get blur class
	blur_class = $(overflow_box).hasClass("vertical") ? "blur-bottom" : "blur-right";
	
	// handle right/bottom blur
	if ($(overflow_box).hasClass("vertical") && (content_size - 5) - overflow_box.scrollTop > $(overflow_box).height() || $(overflow_box).hasClass("horizontal") && (content_size - 5) - overflow_box.scrollLeft > $(overflow_box).width()) {
		$(overflow_box).addClass(blur_class);
	} else {
		$(overflow_box).removeClass(blur_class);
	};
}


// TOGGLE ARTICLE ZEN MODE VIEW
function toggleZenMode() {
	if (!$("#zen_mode").hasClass("visible")) {
		// remove body scrollbar and compensate width with padding to avoid jerk
		$("body")
			.css("overflow", "hidden")
			.css("padding-right", getScrollbarWidth() + "px");
		
		// make zen mode overlay visible
		$("#zen_mode").addClass("visible");
	} else {
		// remove zen mode overlay
		$("#zen_mode").removeClass("visible");

		// wait for overlay to go, then add body scrollbar
		$("#zen_mode").on("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function() {
			if (!$("#zen_mode").hasClass("visible")) {
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


// SELECT CATEGORY
function categorySelect(category) {
	// if any checkbox checked in changed checkbox's container
	if ($(category).closest(".category-container").find(".category-select:checked").length) {
		// highlight selected group's label
		$(category).closest(".dropdown").find(".category-group-label").addClass("selected");
		
		// disable all other checkbox groups
		$(".category-container").not($(category).closest(".category-container")).each(function (e) {
			$(this).find(".category-select").attr("disabled", true);
			$(this).attr("title", "Select categories from only a single group.");
		});
	} else {
		// restore all to normal state
		$(".category-container").attr("title", "");
		$(".category-select").attr("disabled", false);
		$(".category-group-label").removeClass("selected");
	}
}


// POSITION DROPDOWN
function positionDropdown(dropdown) { 
	// get page padding
	var main_container_padding = ($(main_container).innerWidth() - $(main_container).width()) / 2;
		
	// find dropdown
	var dropdown_content = $(dropdown).next(".dropdown-content");

	// get sizes
	var label_width = $(dropdown).outerWidth()
	var dropdown_width = dropdown_content.outerWidth();
	
	// calculate ideal offset
	var center_offset = (label_width - dropdown_width) / 2;
	
	// calculate overflow compensation
	var bounding_box = dropdown.getBoundingClientRect();
	var left_overflow_compensation = calculateOverflowCompensation(bounding_box.left - (main_container_padding - center_offset));
	var right_overflow_compensation = calculateOverflowCompensation((window.innerWidth - bounding_box.right) - (main_container_padding - center_offset));
	
	// apply x position
	dropdown_content.css("transform", "translateX(" + (center_offset - left_overflow_compensation + right_overflow_compensation) +"px)");
}

// CALCULATE OVERFLOW COMPENSATION
function calculateOverflowCompensation(overflow) {
	var absolute_overflow = Math.min(5, overflow);
	return absolute_overflow != 0 ? absolute_overflow - 5 : absolute_overflow;
}

// COPY TEXT TO CLIPBOARD
function copyToClipboard(text) {
	// create dummy textarea and add required text
    var dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = text;
    
    // select text and copy
    dummy.select();
    document.execCommand("copy");
    
    // remove dummy textarea
	document.body.removeChild(dummy);
}