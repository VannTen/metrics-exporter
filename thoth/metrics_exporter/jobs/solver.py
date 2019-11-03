#!/usr/bin/env python3
# thoth-metrics
# Copyright(C) 2018, 2019 Christoph Görn, Francesco Murdaca, Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Solver related metrics."""

import logging

from thoth.storages import GraphDatabase
from thoth.common import OpenShift
import thoth.metrics_exporter.metrics as metrics

from .base import register_metric_job
from .base import MetricsBase

_LOGGER = logging.getLogger(__name__)


class SolverMetrics(MetricsBase):
    """Class to evaluate Metrics for Solvers."""

    _OPENSHIFT = OpenShift()

    @classmethod
    @register_metric_job
    def get_solver_count(cls) -> None:
        """Get number of solvers in Thoth Infra namespace."""
        solvers = len(cls._OPENSHIFT.get_solver_names())

        metrics.graphdb_total_number_solvers.set(solvers)
        _LOGGER.debug("graphdb_total_number_solvers(%r)=%r", solvers)

    @classmethod
    @register_metric_job
    def get_unsolved_python_packages_count(cls) -> None:
        """Get number of unsolved Python packages per solver."""
        graph_db = GraphDatabase()
        graph_db.connect()

        for solver_name in cls._OPENSHIFT.get_solver_names():
            solver_info = graph_db.parse_python_solver_name(solver_name)

            count = graph_db.get_unsolved_python_package_versions_count_all(
                os_name=solver_info["os_name"],
                os_version=solver_info["os_version"],
                python_version=solver_info["python_version"],
            )

            metrics.graphdb_total_number_unsolved_python_packages.labels(solver_name).set(count)
            _LOGGER.debug("graphdb_total_number_unsolved_python_packages(%r)=%r", solver_name, count)

    @staticmethod
    @register_metric_job
    def get_python_packages_solver_error_count() -> None:
        """Get the total number of python packages with solver error True and how many are unparsable or unsolvable."""
        graph_db = GraphDatabase()
        graph_db.connect()

        total_python_packages_solved = graph_db.get_solved_python_packages_count_all(distinct=True)

        total_python_packages_solver_error = graph_db.get_error_solved_python_package_versions_count_all(distinct=True)
        total_python_packages_solver_error_unparseable = graph_db.get_error_solved_python_package_versions_count_all(
            unparseable=True, distinct=True
        )
        total_python_packages_solver_error_unsolvable = graph_db.get_error_solved_python_package_versions_count_all(
            unsolvable=True, distinct=True
        )

        total_python_packages_solved_with_no_error = total_python_packages_solved - total_python_packages_solver_error

        metrics.graphdb_total_python_packages_solved_with_no_error.set(
            total_python_packages_solved_with_no_error
        )
        metrics.graphdb_total_python_packages_with_solver_error_unparseable.set(
            total_python_packages_solver_error_unparseable
        )
        metrics.graphdb_total_python_packages_with_solver_error_unsolvable.set(
            total_python_packages_solver_error_unsolvable
        )
        metrics.graphdb_total_python_packages_with_solver_error.set(total_python_packages_solver_error)

        _LOGGER.debug(
            "graphdb_total_python_packages_solved_with_no_error=%r",
            total_python_packages_solved_with_no_error,
        )

        _LOGGER.debug("graphdb_total_python_packages_with_solver_error=%r", total_python_packages_solver_error)

        _LOGGER.debug(
            "graphdb_total_python_packages_with_solver_error_unparseable=%r",
            total_python_packages_solver_error_unparseable,
        )

        _LOGGER.debug(
            "graphdb_total_python_packages_with_solver_error_unsolvable=%r",
            total_python_packages_solver_error_unsolvable,
        )
