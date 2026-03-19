/**
 * PhdEd – jQuery AJAX navigation and forms (no full page loads)
 */
(function ($) {
    'use strict';

    function ensureLoader() {
        if (document.getElementById('phded-global-loader')) return;
        var loader = document.createElement('div');
        loader.id = 'phded-global-loader';
        loader.className = 'phded-global-loader';
        loader.innerHTML = '' +
            '<div class="phded-loader-card">' +
            '<div class="spinner-border text-info" role="status" aria-hidden="true"></div>' +
            '<div class="phded-loader-text">Loading...</div>' +
            '</div>';
        document.body.appendChild(loader);
    }

    function showLoader() {
        ensureLoader();
        document.getElementById('phded-global-loader').classList.add('is-visible');
    }

    function hideLoader() {
        var loader = document.getElementById('phded-global-loader');
        if (loader) loader.classList.remove('is-visible');
    }

    function setBreadcrumbVisibility(visible) {
        var area = document.getElementById('phded-breadcrumb-area');
        if (!area) return;
        area.style.display = visible ? '' : 'none';
    }

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : null;
    }

    function loadContent(url) {
        showLoader();
        $.ajax({
            url: url,
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function (data) {
                if (data.html) {
                    $('#phded-main-content').html(data.html);
                }
                if (data.breadcrumb_title !== undefined) {
                    $('#phded-breadcrumb-title').text(data.breadcrumb_title);
                }
                if (data.breadcrumb_subtitle !== undefined) {
                    $('#phded-breadcrumb-subtitle').text(data.breadcrumb_subtitle);
                }
                setBreadcrumbVisibility(data.hide_breadcrumb !== true);
            },
            error: function () {
                window.location.href = url;
            },
            complete: function () {
                hideLoader();
            }
        });
    }

    window.loadContent = loadContent;
    window.phdedShowLoader = showLoader;
    window.phdedHideLoader = hideLoader;
    window.phdedSetBreadcrumbVisibility = setBreadcrumbVisibility;

    window.phdedLaunchAssignment = function (button) {
        var url = button && button.getAttribute('data-launch-url');
        if (!url) return;
        showLoader();
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') || '',
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            if (data.success) {
                if (typeof loadContent === 'function' && data.redirect) {
                    loadContent(data.redirect);
                }
            } else {
                alert(data.error || 'Launch failed.');
            }
        }).catch(function () {
            alert('Launch failed.');
        }).finally(function () {
            hideLoader();
        });
    };

    // Sidebar and in-page links: load content via AJAX
    $(document).on('click', 'a.phded-ajax-link', function (e) {
        var href = $(this).attr('href');
        if (!href || href === '#' || href.indexOf('/') !== 0) return;
        e.preventDefault();
        loadContent(href);
    });

    // Logout: AJAX then redirect
    $(document).on('click', 'a.phded-logout-link', function (e) {
        e.preventDefault();
        showLoader();
        $.ajax({
            url: $(this).attr('href'),
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function (data) {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    window.location.href = '/login/';
                }
            },
            error: function () {
                window.location.href = '/login/';
            },
            complete: function () {
                hideLoader();
            }
        });
    });

    // Create user form: submit via AJAX
    $(document).on('submit', '#phded-create-user-form', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $msg = $('#phded-create-user-message');
        $form.find('.form-field-error').text('');
        $msg.hide().removeClass('alert-success alert-danger');
        showLoader();

        $.ajax({
            url: $form.attr('action'),
            method: 'POST',
            data: $form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function (data) {
                if (data.success && data.redirect) {
                    $msg.addClass('alert alert-success').text(data.message || 'Saved.').show();
                    setTimeout(function () {
                        loadContent(data.redirect);
                    }, 1200);
                }
            },
            error: function (xhr) {
                var d = xhr.responseJSON;
                if (d && d.errors) {
                    $.each(d.errors, function (field, msgs) {
                        var $el = $form.find('.form-field-error[data-field="' + field + '"]');
                        $el.text(Array.isArray(msgs) ? msgs[0] : msgs);
                    });
                }
                var msg = (d && d.error) ? d.error : (d && d.errors) ? 'Please fix the errors below.' : 'Something went wrong.';
                $msg.addClass('alert alert-danger').text(msg).show();
            },
            complete: function () {
                hideLoader();
            }
        });
    });

    function submitFormAjax($form, successRedirect) {
        var $msg = $form.find('.alert:first').length ? $form.find('.alert').first() : $form.find('[id$="-message"]').first();
        if (!$msg.length) $msg = $('<div class="alert mb-3" style="display:none;"></div>').prependTo($form);
        $form.find('.form-field-error').text('');
        $msg.hide().removeClass('alert-success alert-danger');
        var data = $form.attr('enctype') === 'multipart/form-data' ? new FormData($form[0]) : $form.serialize();
        showLoader();
        var opts = {
            url: $form.attr('action'),
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function (data) {
                if (data.success && data.redirect) {
                    $msg.addClass('alert-success').text(data.message || 'Saved.').show();
                    setTimeout(function () { loadContent(data.redirect); }, 1200);
                }
            },
            error: function (xhr) {
                var d = xhr.responseJSON;
                if (d && d.errors) {
                    $.each(d.errors, function (field, msgs) {
                        var $el = $form.find('.form-field-error[data-field="' + field + '"]');
                        $el.text(Array.isArray(msgs) ? msgs[0] : msgs);
                    });
                }
                var msg = (d && d.error) ? d.error : 'Please fix the errors below.';
                $msg.addClass('alert-danger').text(msg).show();
            },
            complete: function () {
                hideLoader();
            }
        };
        if (data instanceof FormData) {
            opts.data = data;
            opts.processData = false;
            opts.contentType = false;
        } else {
            opts.data = data;
        }
        $.ajax(opts);
    }

    $(document).on('submit', '#phded-admin-course-form', function (e) {
        e.preventDefault();
        submitFormAjax($(this));
    });

    $(document).on('submit', '#phded-upload-content-form', function (e) {
        e.preventDefault();
        submitFormAjax($(this));
    });

    $(document).on('submit', '#phded-assignment-create-form', function (e) {
        e.preventDefault();
        submitFormAjax($(this));
    });

    $(document).on('click', '.phded-assignment-summary-btn', function () {
        var url = $(this).data('summary-url');
        if (!url) return;
        showLoader();
        $.ajax({
            url: url,
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function (data) {
                $('#phdedAssignmentSummaryContent').html(data.html || '');
                var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('phdedAssignmentSummaryModal'));
                modal.show();
            },
            error: function () {
                alert('Failed to load summary.');
            },
            complete: function () {
                hideLoader();
            }
        });
    });

    $(document).on('click', '.phded-student-response-btn', function () {
        var url = $(this).data('response-url');
        if (!url) return;
        showLoader();
        $.ajax({
            url: url,
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function (data) {
                $('#phdedStudentResponseContent').html(data.html || '');
                var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('phdedStudentResponseModal'));
                modal.show();
            },
            error: function () {
                alert('Failed to load student response.');
            },
            complete: function () {
                hideLoader();
            }
        });
    });
})(jQuery);
