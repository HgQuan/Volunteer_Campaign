document.addEventListener('DOMContentLoaded', function() {
    const donationTypeField = document.querySelector('#id_type');
    const moneyField = document.querySelector('#id_money');
    const productField = document.querySelector('#id_product');

    function toggleFields() {
        if (donationTypeField.value === 'money') {
            moneyField.closest('.form-row').style.display = '';
            moneyField.disabled = false;
            productField.closest('.form-row').style.display = 'none';
            productField.disabled = true;
        } else if (donationTypeField.value === 'product') {
            productField.closest('.form-row').style.display = '';
            productField.disabled = false;
            moneyField.closest('.form-row').style.display = 'none';
            moneyField.disabled = true;
        } else {
            moneyField.closest('.form-row').style.display = '';
            moneyField.disabled = false;
            productField.closest('.form-row').style.display = '';
            productField.disabled = false;
        }
    }

    toggleFields();

    donationTypeField.addEventListener('change', toggleFields);
});

