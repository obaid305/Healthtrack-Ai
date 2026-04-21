// HealthTrack AI - Main JavaScript (cleaned)
$(document).ready(function() {
    // Back to Top Button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#backToTop').fadeIn();
        } else {
            $('#backToTop').fadeOut();
        }
    });
    
    $('#backToTop').click(function() {
        $('html, body').animate({ scrollTop: 0 }, 500);
        return false;
    });
    
    // Form validation
    $('form').on('submit', function(e) {
        let isValid = true;
        $(this).find('[required]').each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        if ($('#password').length && $('#confirm_password').length) {
            if ($('#password').val() !== $('#confirm_password').val()) {
                $('#confirm_password').addClass('is-invalid');
                showAlert('Passwords do not match', 'danger');
                isValid = false;
            }
        }
        if (!isValid) e.preventDefault();
    });
    
    window.showAlert = function(message, type) {
        const alertHtml = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : (type === 'danger' ? 'exclamation-circle' : 'info-circle')} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
        $('.container').first().before(alertHtml);
        setTimeout(function() {
            $('.alert').fadeOut(300, function() { $(this).remove(); });
        }, 5000);
    };
    
    // Load time slots (used in book_appointment.html)
    window.loadTimeSlots = function(doctorId, date, selectElementId) {
        if (!date) return;
        const select = $('#' + selectElementId);
        select.html('<option value="">Loading...</option>');
        $.ajax({
            url: '/get-available-slots',
            method: 'POST',
            data: { doctor_id: doctorId, date: date },
            success: function(response) {
                select.empty();
                select.append('<option value="">Select a time</option>');
                if (response.slots && response.slots.length > 0) {
                    response.slots.forEach(function(slot) {
                        select.append('<option value="' + slot + '">' + slot + '</option>');
                    });
                } else {
                    select.append('<option value="">No slots available</option>');
                }
            },
            error: function() {
                select.html('<option value="">Error loading slots</option>');
                showAlert('Error loading available slots', 'danger');
            }
        });
    };
    
    // Cancel appointment (global function used in appointments.html)
    window.cancelAppointment = function(id) {
        currentAppointmentId = id;
        $('#cancelReason').val('');
        $('#cancelModal').modal('show');
    };
    
    $('#confirmCancel').click(function() {
        const reason = $('#cancelReason').val();
        $.ajax({
            url: '/cancel-appointment/' + currentAppointmentId,
            method: 'POST',
            data: { reason: reason },
            success: function(response) {
                if (response.success) {
                    $('#cancelModal').modal('hide');
                    showAlert('Appointment cancelled successfully', 'success');
                    setTimeout(function() { location.reload(); }, 1500);
                } else {
                    showAlert(response.message || 'Error cancelling appointment', 'danger');
                }
            },
            error: function() {
                showAlert('Error cancelling appointment', 'danger');
            }
        });
    });
    
    // Reschedule appointment (fixed time picker)
    window.rescheduleAppointment = function(id) {
        currentAppointmentId = id;
        $('#newDate').val('');
        $('#newTime').val('');
        $('#rescheduleModal').modal('show');
    };
    
    $('#confirmReschedule').click(function() {
        const newDate = $('#newDate').val();
        let newTime = $('#newTime').val();
        if (!newDate || !newTime) {
            showAlert('Please select both date and time', 'warning');
            return;
        }
        // Convert 24h time to 12h format with AM/PM if needed
        if (newTime.match(/^\d{2}:\d{2}$/)) {
            let [hour, minute] = newTime.split(':');
            hour = parseInt(hour);
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const hour12 = hour % 12 || 12;
            newTime = `${hour12}:${minute} ${ampm}`;
        }
        $.ajax({
            url: '/reschedule-appointment/' + currentAppointmentId,
            method: 'POST',
            data: { new_date: newDate, new_time: newTime },
            success: function(response) {
                if (response.success) {
                    $('#rescheduleModal').modal('hide');
                    showAlert('Appointment rescheduled successfully', 'success');
                    setTimeout(function() { location.reload(); }, 1500);
                } else {
                    showAlert(response.message || 'Error rescheduling appointment', 'danger');
                }
            },
            error: function() {
                showAlert('Error rescheduling appointment', 'danger');
            }
        });
    });
    
    // Date picker min date
    $('input[type="date"]').each(function() {
        const today = new Date().toISOString().split('T')[0];
        $(this).attr('min', today);
    });
    
    $('[data-bs-toggle="tooltip"]').tooltip();
    setTimeout(function() {
        $('.alert').fadeOut(300, function() { $(this).remove(); });
    }, 5000);
});

let currentAppointmentId = null;

$(window).scroll(function() {
    if ($(this).scrollTop() > 300) {
        $('#backToTop').fadeIn(300).css('display', 'flex');
    } else {
        $('#backToTop').fadeOut(300);
    }
});

$('#backToTop').click(function() {
    $('html, body').animate({ scrollTop: 0 }, 500);
    return false;
});