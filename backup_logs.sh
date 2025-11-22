#!/usr/bin/env bash
set -euo pipefail

# CONFIG
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
BACKUP_DIR="${PROJECT_ROOT}/backups"
RETENTION=7   # keep last N backups

mkdir -p "$BACKUP_DIR"
now=$(date +"%F-%H%M%S")
tarfile="${BACKUP_DIR}/logs-${now}.tgz"
encfile="${tarfile}.gpg"

echo "[1] Creating tar: $tarfile ..."
tar -C "$PROJECT_ROOT" -czf "$tarfile" "$(basename "$LOG_DIR")"

echo "[2] Encrypting with gpg (interactive passphrase). Use a strong passphrase."
# interactive mode: gpg will prompt for passphrase
gpg --symmetric --cipher-algo AES256 -o "$encfile" "$tarfile"

# make sure encrypted file exists
if [[ ! -f "$encfile" ]]; then
  echo "ERROR: encryption failed, no $encfile" >&2
  exit 2
fi

# remove plaintext tar (zero-risk) - keep only encrypted file
shred -u -v "$tarfile" || rm -f "$tarfile"

# tighten permissions
chmod 600 "$encfile"

# prune old backups (by encrypted file names)
echo "[3] Pruning backups, keeping last $RETENTION ..."
ls -1t "${BACKUP_DIR}"/logs-*.tgz.gpg 2>/dev/null | tail -n +$((RETENTION+1)) | xargs -r rm -v --

echo "[done] Encrypted backup written: $encfile"

