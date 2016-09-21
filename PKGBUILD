# Maintainer: Alexander F Rødseth <xyproto@archlinux.org>

pkgname=duckling-git
pkgver=6b6eb7c
pkgrel=1
pkgdesc='Weird 2D platform game'
arch=('x86_64' 'i686')
url='http://github.com/xyproto/duckling'
license=('MIT')
depends=('python2' 'python2-pygame')
makdepends=('setconf' 'gendesk' 'git')
conflicts=('duckling')
provides=('duckling')
source=('duckling::git://github.com/xyproto/duckling.git')
md5sums=('SKIP')
_gfxdir='/usr/share/duckling/gfx'

pkgver() {
  cd "${pkgname%-git}"

  git describe --always | sed 's|-|.|g'
}

prepare() {
  cd "${pkgname%-git}"

  setconf duckling.py GFX_DIR "\"$_gfxdir\""
  gendesk -f -n --pkgname duckling --pkgdesc "$pkgdesc"
}

package() {
  cd "${pkgname%-git}"

  install -d "${pkgdir}$_gfxdir"
  install -Dm644 gfx/* "${pkgdir}$_gfxdir"
  install -Dm755 duckling.py "$pkgdir/usr/bin/duckling"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  install -Dm644 gfx/player.png "$pkgdir/usr/share/pixmaps/duckling.png"
  install -Dm644 duckling.desktop \
    "$pkgdir/usr/share/applications/duckling.desktop"
}

# vim:set ts=2 sw=2 et:
