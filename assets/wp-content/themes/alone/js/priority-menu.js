(function ($) {
    'use strict';

	$( document ).ready(function() {
		/**
		 * Menu Mobile
		 */

		$('.site-branding').on('click', '.menu-toggle', function (event) {
			event.preventDefault();
			$(this).toggleClass('toggled-on');
			$('.primary-navigation').toggleClass('show-menu');
			$('.primary-navigation .expanded').find('ul').slideUp();
			$('.primary-navigation').find('li').removeClass('expanded');
		});

		$('.primary-navigation').find('.page_item_has_children > a, .menu-item-has-children > a').append('<span class="sub-menu-toggle">On</span>');

		$('.primary-navigation').on('click', '.sub-menu-toggle', function (event) {
			event.preventDefault();
			openSubMenu($(this));

		});


		$(window).on('resize', function () {
		  if (window.matchMedia( '(min-width: 992px)' ).matches) {
		      $('.menu-toggle').removeClass('toggled-on');
					$('.primary-navigation').removeClass('show-menu');
					$('.primary-navigation .expanded').find('ul').slideUp();
					$('.primary-navigation').find('li').removeClass('expanded');
		  }

		});

	});



	/**
	 * Open sub menu
	 */
	function openSubMenu($el) {
	  $el.closest('li').siblings().find('ul').slideUp();
	  $el.closest('li').siblings().removeClass('expanded');
	  $el.closest('li').siblings().find('li').removeClass('expanded');

	  $el.closest('li').children('ul').slideToggle();
	  $el.closest('li').toggleClass('expanded');
	}

})
(jQuery);
