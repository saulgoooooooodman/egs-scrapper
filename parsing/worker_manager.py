from __future__ import annotations

from PySide6.QtCore import QThread


class WorkerManager:
    def _ensure_thread_store(self):
        if not hasattr(self, "_threads"):
            self._threads = []
        if not hasattr(self, "_workers"):
            self._workers = []

    def start_worker(self, worker):
        self._ensure_thread_store()

        thread = QThread(self)
        worker.moveToThread(thread)

        self._threads.append(thread)
        self._workers.append(worker)

        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)

        worker.finished.connect(self.on_worker_finished)
        worker.progress.connect(self.on_worker_progress)
        worker.error.connect(self.on_worker_error)

        worker.finished.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        def cleanup():
            if worker in self._workers:
                self._workers.remove(worker)
            if thread in self._threads:
                self._threads.remove(thread)

        thread.finished.connect(cleanup)
        thread.start()

    def stop_all_workers(self):
        self._ensure_thread_store()

        for thread in list(self._threads):
            try:
                if thread.isRunning():
                    thread.quit()
                    thread.wait(3000)
            except Exception:
                pass

        self._threads.clear()
        self._workers.clear()