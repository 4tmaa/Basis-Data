document.addEventListener('DOMContentLoaded', () => {
    // Validasi form peminjaman film
    const formPinjam = document.querySelector('#formPinjam');
    
    if (formPinjam) {
        formPinjam.addEventListener('submit', (event) => {
            const lamaPinjam = formPinjam.querySelector('input[name="lama_pinjam"]').value;
            if (isNaN(lamaPinjam) || lamaPinjam <= 0) {
                event.preventDefault();
                alert('Lama pinjam harus berupa angka yang lebih dari 0.');
            }
        });
    }
    
    // Animasi tombol saat hover
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            button.style.transform = 'scale(1.05)';
        });
        
        button.addEventListener('mouseout', () => {
            button.style.transform = 'scale(1)';
        });
    });
});
