let regolamento = $("a:contains('Regolamento')");
// Se esiste
if (regolamento.length) {
    regolamento.attr("href", "https://datafiles.gaia.cri.it/media/filer_public/08/59/0859cd54-ddad-4f26-8f8d-f48d2c92801d/regolamento_dei_corsi_di_formazione_per_volontari_e_dipendenti_della_croce_rossa_italiana.pdf\n")
    regolamento.attr('target', '_blank');
}
