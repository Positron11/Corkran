$(function () {
	// initialize page
	truncateAnnouncement();
	calculateProgressBar();

	// toggle mobile navbar links
	$(document).on('click', '.menu-btn', function (e) {
		e.preventDefault();
		$(".navbar").toggleClass("mobile-show");
	});

	// toggle comment reply box
	$(document).on('click', '.toggle-btn.reply', function (e) {
		e.preventDefault();
		toggleCommentEditor("reply", $(this));
	});

	// toggle comment edit box
	$(document).on('click', '.toggle-btn.edit', function (e) {
		e.preventDefault();
		toggleCommentEditor("edit", $(this));
	});

	// on scroll...
	$(window).on("scroll", function () {
		calculateProgressBar();
	});

	// on resize...
	$(window).on("resize", function () {
		truncateAnnouncement();
	});

	// prevent empty textarea
	$("textarea").each(function () {
		$(this).on("keydown", function (e) {
			var c = $(this).val().length;

			// prevent directly typing leading spaces or newlines
			if (c == 0)
				return (e.which !== "13" && e.which !== 32);

			// disable submit button if empty
			$(this).parent().find("button").prop("disabled", ($.trim($(this).val()) == ""));
		});
	});

	// Automatically resize textarea
	$("textarea").on('input', function () {
		this.style.height = 'auto';
		this.style.height = (this.scrollHeight) + 5 + 'px';
	});

	// fade out and remove alert
	if ($(".alert").length) {
		$(".alert").css("opacity", "0");
		$(".alert").on('transitionend webkitTransitionEnd oTransitionEnd otransitionend MSTransitionEnd', function (e) {
			$(this).css("transition", "0.3s ease-out");
			$(this).css("height", "0px");
			$(this).css("margin", "0px");
			$(this).css("padding", "0px");
			$(".alert").on('transitionend webkitTransitionEnd oTransitionEnd otransitionend MSTransitionEnd', function (e) {
				$(this).hide();
			})
		})
	}
});

// CALCULATE PROGRESS BAR
function calculateProgressBar() {
	// if on article detail page...
	if ($(".main.article").length) {
		var bottom_height = $(document).height() - $(".main.article .content").outerHeight() - 127;
		// if the article is substantially larger than page
		if (bottom_height > $(window).height()) {
			var height = $(".main.article .content").outerHeight();
			var y_offset = -($(".main.article .content").offset().top - $(window).scrollTop() - 127);
			var completed = y_offset / height * 100;
		} else {
			var y_offset = window.pageYOffset;
			var height = $(document).height() - $(window).height();
			var completed = y_offset / height * 100;
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
function truncateAnnouncement() {
	// approximate fixed value for distance from top of sidebar to bottom of page
	var height = window.innerHeight - 380;

	// set sidebar height
	$('.sidebar .announcement').css("height", height);
}

// TOGGLE COMMENT EDITORS
function toggleCommentEditor(editor, button) {
	if (editor == "reply") {
		var type = ".reply";
		var text = "Reply";
		var other = ".edit";
		var other_text = "Edit";
	} else {
		var type = ".edit";
		var text = "Edit";
		var other = ".reply";
		var other_text = "Reply"
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
}