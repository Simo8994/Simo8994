// Archivio minimale su file JSON. Sufficiente per un prototipo, non per la produzione.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export function createStore(file) {
  let data = { bills: [] };
  if (file && fs.existsSync(file)) {
    data = JSON.parse(fs.readFileSync(file, 'utf8'));
  }

  function save() {
    if (!file) return;
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const tmp = `${file}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
    fs.renameSync(tmp, file);
  }

  return {
    list(filter = () => true) {
      return data.bills.filter(filter);
    },
    get(id) {
      return data.bills.find((b) => b.id === id) || null;
    },
    create(fields) {
      const bill = {
        id: crypto.randomUUID(),
        status: 'pending', // pending -> open -> paid | rejected
        createdAt: new Date().toISOString(),
        ...fields,
      };
      data.bills.push(bill);
      save();
      return bill;
    },
    update(id, patch) {
      const bill = this.get(id);
      if (!bill) return null;
      Object.assign(bill, patch);
      save();
      return bill;
    },
  };
}
