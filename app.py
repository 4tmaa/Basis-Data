from flask import Flask, render_template, request, redirect, url_for, flash
from mysql import connector
from forms import TambahFilmForm  # Assuming you have forms.py
from datetime import date

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages

# Fungsi untuk membuat koneksi ke database
def get_db_connection():
    return connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="1025_rentaldvd"
    )

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/film/<string:id>', methods=['GET', 'POST'])
def film_detail(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Retrieve film details
    cursor.execute("SELECT * FROM film WHERE Kode_Film = %s;", (id,))
    film = cursor.fetchone()

    if request.method == 'POST':
        # Get data from form
        no_id = request.form['no_id']  # Get No_Id (Penyewa's ID)
        nama = request.form['nama']  # Get Nama from form
        alamat = request.form['alamat']  # Get Alamat from form
        jenis_id = request.form['Jenis_Id']  # Get Jenis_Id from form
        
        # Check if the Jenis_Id exists in the identitas table
        cursor.execute("SELECT * FROM identitas WHERE Kode = %s;", (jenis_id,))
        identitas = cursor.fetchone()

        if not identitas:
            flash('Jenis_Id tidak valid!', 'danger')  # Show an error if Jenis_Id is not valid
            return redirect(url_for('film_detail', id=id))

        # Check if No_Id exists in the member table
        cursor.execute("SELECT * FROM member WHERE No_Id = %s;", (no_id,))
        member = cursor.fetchone()

        if not member:
            # If No_Id does not exist in member table, insert it
            cursor.execute("""
                INSERT INTO member (No_Id, Jenis_Id, Nama, Alamat)
                VALUES (%s, %s, %s, %s);
            """, (no_id, jenis_id, nama, alamat))  # Insert new Penyewa details
            db.commit()

        # Proceed with the transaction if Penyewa exists or after inserting it
        tanggal_pinjam = date.today()
        tanggal_kembali = tanggal_pinjam  # You can modify this if you have a rule for return date
        total_bayar = 10000  # Example rent cost
        denda = 0  # Example fine

        # Insert transaction record into 'transaksi' table
        cursor.execute("""
            INSERT INTO transaksi (Penyewa, Film, Tanggal_Pinjam, Tanggal_Kembali, Total_bayar, Denda, Tanggal_Kembali_Aktual)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (no_id, film[0], tanggal_pinjam, tanggal_kembali, total_bayar, denda, None))
        db.commit()

        # Update film stock after transaction
        cursor.execute("UPDATE film SET Stok = Stok - 1 WHERE Kode_Film = %s;", (id,))
        db.commit()

        cursor.close()

        # After processing the POST request, redirect to films list
        return redirect(url_for('films'))  # Redirect to films list after borrowing the film

    # Pre-populate Penyewa's data if it's a GET request
    if request.method == 'GET':
        no_id = ''  # Empty penyewa in case of first visit
        penyewa_details = {}  # Empty dictionary to store the details of the penyewa
        return render_template('film_detail.html', film=film, no_id=no_id, penyewa_details=penyewa_details)

    cursor.close()
    return render_template('film_detail.html', film=film)

@app.route('/film/edit/<string:id>', methods=['GET', 'POST'])
def edit_film(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Retrieve film details
    cursor.execute("SELECT * FROM film WHERE Kode_Film = %s;", (id,))
    film = cursor.fetchone()

    if request.method == 'POST':
        # Get updated film details from the form
        new_judul = request.form['judul']
        new_genre = request.form['genre']
        new_stok = request.form['stok']
        new_poster_url = request.form['poster_url']

        # Update the film details in the database
        cursor.execute("""
            UPDATE film 
            SET Judul = %s, Genre = %s, Stok = %s, Poster_URL = %s 
            WHERE Kode_Film = %s;
        """, (new_judul, new_genre, new_stok, new_poster_url, id))
        db.commit()

        flash('Film berhasil diperbarui!', 'success')
        return redirect(url_for('film_detail', id=id))  # Redirect to the updated film detail page

    cursor.close()
    return render_template('edit_film.html', film=film)

@app.route('/film/delete/<string:id>', methods=['POST'])
def delete_film(id):
    db = get_db_connection()
    cursor = db.cursor()

    # Delete the film from the database
    cursor.execute("DELETE FROM film WHERE Kode_Film = %s;", (id,))
    db.commit()

    cursor.close()

    flash('Film berhasil dihapus!', 'danger')
    return redirect(url_for('films'))  # Redirect to the films list after deleting the film


@app.route('/films', methods=['GET', 'POST'])
def films():
    db = get_db_connection()
    cursor = db.cursor()

    # Ambil daftar genre yang tersedia untuk filter
    cursor.execute("SELECT DISTINCT Genre FROM film;")
    genres = cursor.fetchall()

    # Filter film berdasarkan genre yang dipilih (jika ada)
    if request.method == 'POST':
        selected_genre = request.form.get('genre')
        
        if selected_genre:  # Jika genre dipilih
            cursor.execute("SELECT Kode_Film, Judul, Poster_URL, Genre FROM film WHERE Genre = %s;", (selected_genre,))
        else:  # Jika tidak ada genre yang dipilih (Semua Genre)
            cursor.execute("SELECT Kode_Film, Judul, Poster_URL, Genre FROM film;")

    else:  # Untuk GET, menampilkan semua film tanpa filter
        cursor.execute("SELECT Kode_Film, Judul, Poster_URL, Genre FROM film;")

    result = cursor.fetchall()
    cursor.close()
    
    return render_template('films.html', hasil=result, genres=genres)

@app.route('/tambah-film', methods=['GET', 'POST'])
def tambah_film():
    form = TambahFilmForm()

    if form.validate_on_submit():  # Menangani form yang dikirim
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO film (Kode_Film, Judul, Genre, Jml_Keping, Stok, Poster_URL)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (form.kode_film.data, form.judul.data, form.genre.data, form.jml_keping.data, form.stok.data, form.poster_url.data))
        db.commit()
        cursor.close()

        flash('Film berhasil ditambahkan!', 'success')  # Menampilkan pesan sukses
        return redirect(url_for('films'))  # Redirect ke daftar film

    return render_template('tambah_film.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
