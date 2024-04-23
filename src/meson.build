pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'audiolang'
gnome = import('gnome')

gnome.compile_resources('audiolang',
  'audiolang.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'audiolang.in',
  output: 'audiolang',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

audiolang_sources = [
  '__init__.py',
  'main.py',
  'choose_dir.py',
  'word_preview.py',
  'feedback_window.py'
]

install_data(audiolang_sources, install_dir: moduledir)
