from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class TambahFilmForm(FlaskForm):
    kode_film = StringField('Kode Film', validators=[DataRequired()])
    judul = StringField('Judul', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    jml_keping = IntegerField('Jumlah Keping', validators=[DataRequired()])
    stok = IntegerField('Stok', validators=[DataRequired()])
    poster_url = StringField('Poster URL')

    submit = SubmitField('Tambah Film')
