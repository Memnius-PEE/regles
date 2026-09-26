"""Chaque garde est testée dans les deux sens : elle accepte un dépôt sain et refuse un cas fautif.

Lancer : MEMNIUS_REGISTRE=<clone de Memnius-PEE/registre> python3 -m unittest discover -s tests -v
Sans MEMNIUS_REGISTRE, le dossier voisin ../registre est essayé (disposition du kit) ; les tests de A3
échouent s'il est introuvable, car une garde qui ne peut pas tourner ne doit jamais passer pour verte.
"""
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

GARDES = Path(__file__).resolve().parent.parent / "gardes" / "gardes.py"
REGISTRE = os.environ.get("MEMNIUS_REGISTRE") or str(GARDES.parent.parent.parent / "registre")

FICHE = textwrap.dedent("""\
    schema: memnius/1
    id: {id}
    titre: Sujet de test
    resume: Un sujet minimal qui respecte le socle, pour tester les gardes.
    statut: actif
    nature: etude
    domaines: [physique]
    langue: fr
    mainteneurs:
      - github: mainteneur-test
    agents:
      politique: relecture-humaine
    socle:
      version: v1
      niveau: socle
      options: []
    licence: CC-BY-4.0
    visibilite: public
    cree_le: 2026-09-26
    """)

ENTREE = textwrap.dedent("""\
    # {n} — Adopter le socle

    - Date : 2026-09-26
    - Origine : [humain] « on adopte le socle »
    - Décidé par : @mainteneur-test
    - Remplace : —
    """)


def sh(dossier, *args):
    subprocess.run(args, cwd=dossier, check=True, capture_output=True)


class DepotDeTest(unittest.TestCase):
    """Crée un dépôt Git sain dans un dossier temporaire nommé comme son id."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = Path(self._tmp.name) / "sujet-test"
        self.d.mkdir()
        fichiers = {
            "README.md": "# Sujet de test\n\nVoir la règle C2 et la garde A4.\n",
            "AGENTS.md": "# Agents\n\nAppliquer C1–C10 ; R2 si des agents écrivent.\n",
            "CONTRIBUTING.md": "# Contribuer\n",
            "PASSATION.md": "# Passation\n\n## 5. Ce qui reste dû ou en cours *\n- rien\n",
            ".github/workflows/memnius.yml": "name: Memnius\n",
            "memnius.yaml": FICHE.format(id="sujet-test"),
            "decisions/0001-adopter-le-socle.md": ENTREE.format(n="0001"),
            "notes/idee.md": "Une note ordinaire qui parle de C99 sans être un fichier de gouvernance.\n",
        }
        for chemin, texte in fichiers.items():
            (self.d / chemin).parent.mkdir(parents=True, exist_ok=True)
            (self.d / chemin).write_text(texte, encoding="utf-8")
        sh(self.d, "git", "init", "-q", "-b", "main")
        sh(self.d, "git", "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
        sh(self.d, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "initial")
        self.base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.d, capture_output=True, text=True).stdout.strip()

    def tearDown(self):
        self._tmp.cleanup()

    def ecrire(self, chemin, texte, commit=True):
        p = self.d / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
        sh(self.d, "git", "add", "-A")
        if commit:
            sh(self.d, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "changement")

    def gardes(self, *options, registre=REGISTRE):
        cmd = [sys.executable, str(GARDES), str(self.d), *options]
        if registre:
            cmd += ["--registre", registre]
        r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "MEMNIUS_REGISTRE": ""})
        return r.returncode, r.stdout

    def assertVerte(self, garde, *options, **kw):
        code, sortie = self.gardes("--seulement", garde, *options, **kw)
        self.assertIn(f"[ ok ] {garde}", sortie, sortie)
        self.assertEqual(code, 0, sortie)

    def assertSonne(self, garde, motif, *options, **kw):
        code, sortie = self.gardes("--seulement", garde, *options, **kw)
        self.assertIn(f"[FIRE] {garde}", sortie, sortie)
        self.assertIn(motif, sortie)
        self.assertEqual(code, 1, sortie)


class Ensemble(DepotDeTest):
    def test_depot_sain_toutes_vertes(self):
        code, sortie = self.gardes("--base", self.base)
        self.assertEqual(code, 0, sortie)
        self.assertIn("Bilan : 5/5 gardes vertes", sortie)


class A2Secrets(DepotDeTest):
    def test_sain(self):
        self.assertVerte("A2")

    def test_jeton_gitlab(self):
        self.ecrire("travaux/config.py", 'URL = "x"\nJETON = "glpat-' + "a" * 20 + '"\n', commit=False)
        self.assertSonne("A2", "travaux/config.py:2 : jeton GitLab")

    def test_mot_de_passe_en_clair(self):
        self.ecrire("notes/acces.md", 'password = "correcthorsebattery"\n', commit=False)  # memnius:autorise (faux secret de test)
        self.assertSonne("A2", "mot de passe")

    def test_fichier_env(self):
        self.ecrire(".env", "RIEN=1\n", commit=False)
        self.assertSonne("A2", ".env : fichier de secrets")

    def test_faux_positif_autorise(self):
        self.ecrire("docs/exemple.md", 'token = "exemple-de-jeton-factice"  <!-- memnius:autorise -->\n', commit=False)
        self.assertVerte("A2")


class A3Structure(DepotDeTest):
    def test_sain(self):
        self.assertVerte("A3")

    def test_passation_absente(self):
        (self.d / "PASSATION.md").unlink()
        self.assertSonne("A3", "PASSATION.md")

    def test_fiche_invalide(self):
        self.ecrire("memnius.yaml", FICHE.format(id="sujet-test").replace("statut: actif", "statut: fini"))
        self.assertSonne("A3", "statut")

    def test_socle_manquant(self):
        fiche = FICHE.format(id="sujet-test").split("socle:")[0] + "licence: CC-BY-4.0\nvisibilite: public\ncree_le: 2026-09-26\n"
        self.ecrire("memnius.yaml", fiche)
        self.assertSonne("A3", "socle")

    def test_registre_introuvable_compte_comme_echec(self):
        self.assertSonne("A3", "n'a pas pu tourner", registre=None)


class A4Journal(DepotDeTest):
    def test_sain_avec_nouvelle_entree(self):
        self.ecrire("decisions/0002.md", ENTREE.format(n="0002"))
        self.assertVerte("A4", "--base", self.base)

    def test_entree_publiee_modifiee(self):
        self.ecrire("decisions/0001-adopter-le-socle.md", ENTREE.format(n="0001") + "Ajout après coup.\n")
        self.assertSonne("A4", "entrée publiée modifiée", "--base", self.base)

    def test_entree_du_gabarit_remplie(self):
        # Sujet créé avec « Use this template » : la première pull request remplit l'entrée 0001.
        self.ecrire("decisions/0001-adopter-le-socle.md", ENTREE.format(n="0001").replace("2026-09-26", "AAAA-MM-JJ"))
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.d, capture_output=True, text=True).stdout.strip()
        self.ecrire("decisions/0001-adopter-le-socle.md", ENTREE.format(n="0001"))
        self.assertVerte("A4", "--base", base)

    def test_entree_publiee_supprimee(self):
        (self.d / "decisions/0001-adopter-le-socle.md").unlink()
        self.ecrire("decisions/0002.md", ENTREE.format(n="0002"))
        self.assertSonne("A4", "entrée publiée", "--base", self.base)  # vue par Git comme supprimée ou renommée

    def test_sans_marqueur_origine(self):
        self.ecrire("decisions/0002.md", ENTREE.format(n="0002").replace("[humain] ", ""))
        self.assertSonne("A4", "[humain], [choix] ou [agent]")

    def test_nom_non_conforme(self):
        self.ecrire("decisions/choix-du-format.md", ENTREE.format(n="0002"))
        self.assertSonne("A4", "nom attendu")

    def test_valeurs_du_gabarit(self):
        self.ecrire("decisions/0002.md", ENTREE.format(n="0002").replace("2026-09-26", "AAAA-MM-JJ"))
        self.assertSonne("A4", "gabarit")

    def test_base_introuvable_compte_comme_echec(self):
        self.assertSonne("A4", "n'a pas pu tourner", "--base", "f" * 40)


class A5Renvois(DepotDeTest):
    def test_sain(self):
        self.assertVerte("A5")

    def test_regle_inexistante(self):
        self.ecrire("AGENTS.md", "# Agents\n\nVoir la règle C11.\n")
        self.assertSonne("A5", "C11 n'existe pas")

    def test_option_inconnue(self):
        self.ecrire("memnius.yaml", FICHE.format(id="sujet-test").replace("options: []", "options: [O9]"))
        self.assertSonne("A5", "option du socle inconnue : O9")

    def test_regle_abrogee(self):
        sys.path.insert(0, str(GARDES.parent))
        import gardes as module
        ancien = module.REGLES
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(ancien.read_text(encoding="utf-8").replace(
                "C2: {titre: Décision écrite, niveau: socle}", "C2: {titre: Décision écrite, niveau: socle, abrogee: true}"))
        module.REGLES = Path(f.name)
        try:
            with self.assertRaises(module.Feu) as feu:
                module.garde_a5(self.d, module.fichiers_suivis(self.d))
            self.assertIn("C2 est abrogée", str(feu.exception))
        finally:
            module.REGLES = ancien
            os.unlink(f.name)


class A6GrosFichiers(DepotDeTest):
    def test_sain(self):
        self.ecrire("donnees/brut/mesures.csv", "x,y\n" * 1000, commit=False)
        self.assertVerte("A6")

    def test_fichier_de_11_mo(self):
        (self.d / "donnees/brut").mkdir(parents=True, exist_ok=True)
        (self.d / "donnees/brut/gros.bin").write_bytes(os.urandom(11_000_000))
        sh(self.d, "git", "add", "-A")
        self.assertSonne("A6", "donnees/brut/gros.bin (11.0 Mo)")

    def test_pointeur_lfs_accepte(self):
        pointeur = "version https://git-lfs.github.com/spec/v1\noid sha256:" + "0" * 64 + "\nsize 50000000\n"
        self.ecrire("donnees/brut/gros.h5", pointeur, commit=False)
        self.assertVerte("A6")


if __name__ == "__main__":
    unittest.main()
