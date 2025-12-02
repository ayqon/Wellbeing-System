document.addEventListener('DOMContentLoaded', function () {
    // Tab Switching Logic
    const tabs = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active', 'show'));

            // Add active class to clicked tab
            tab.classList.add('active');

            // Show corresponding content
            const targetId = tab.getAttribute('data-target');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active', 'show');
            }
        });
    });

    // Bulk Selection Logic
    const selectAllCheckbox = document.getElementById('selectAll');
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
    const selectedCountSpan = document.getElementById('selectedCount');

    function updateBulkActionState() {
        const selectedCount = Array.from(userCheckboxes).filter(cb => cb.checked).length;

        if (selectedCount > 0) {
            bulkDeleteBtn.disabled = false;
            bulkDeleteBtn.style.display = 'inline-flex'; // Show button
            if (selectedCountSpan) selectedCountSpan.textContent = `(${selectedCount})`;
        } else {
            bulkDeleteBtn.disabled = true;
            bulkDeleteBtn.style.display = 'none'; // Hide button
            if (selectedCountSpan) selectedCountSpan.textContent = '';
        }

        // Update "Select All" state
        if (selectedCount === userCheckboxes.length && userCheckboxes.length > 0) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedCount > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const isChecked = this.checked;
            userCheckboxes.forEach(cb => {
                cb.checked = isChecked;
            });
            updateBulkActionState();
        });
    }

    userCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateBulkActionState);
    });
});
