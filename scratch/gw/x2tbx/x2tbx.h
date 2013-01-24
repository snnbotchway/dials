/* x2tbx
 *
 * a toolbox to gracefully handle unmerged reflections for (in the first
 * instance) calculations in PyChef and resolution limits. N.B. will have
 * fundamental data structures:
 *
 * observation - float I, float sigI, float property, int flag
 *
 * unmerged_reflections - map(cctbx::miller::index, std::vector<observation>)
 *
 * though ideally want these nicely available from Python too (though that I
 * can live without.)
 *
 * first task try just implementing one calculation for e.g. resolution limits.
 *
 */

#include <boost/python.hpp>
#include <scitbx/array_family/shared.h>
#include <scitbx/array_family/flex_types.h>
#include <miller.h>
#include <uctbx.h>
#include <cctype>
#include <map>
#include <algorithm>
#include <vector>

namespace cmil = cctbx::miller;
namespace cuc = cctbx::uctbx;

namespace x2tbx {

  struct observation {
    float I;
    float sigI;
    float property;
    int flag;
  };

  struct merged_isig {
    float I;
    float sigI;
  };

  typedef std::vector<observation> observation_list;

  typedef scitbx::af::tiny<float, 2> i_sig_type;

  class ObservationList {
  public:
    ObservationList(void);
    ~ObservationList(void);

    void add(i_sig_type);
    void merge(void);
    i_sig_type i_sigma(void);
    size_t multiplicity(void);
    float rmerge(void);

  private:
    scitbx::af::shared<i_sig_type> observations;
    float imean, sigimean;
  };

  typedef cmil::index<int> miller_index_type;
  typedef scitbx::af::const_ref<miller_index_type> miller_index_list_type;
  typedef scitbx::af::const_ref<float> float_value_list_type;

  class ReflectionList {
  public:
    ReflectionList();
    ~ReflectionList();

    void setup(miller_index_list_type,
               float_value_list_type,
               float_value_list_type);
    void merge(void);
    float i_sigma(void);
    float rmerge(void);

  private:
    std::map<miller_index_type, ObservationList> reflections;
  };

  typedef std::map<cctbx::miller::index<int>, observation_list> \
    unmerged_reflections;
  typedef std::map<cctbx::miller::index<int>, observation_list>::iterator \
    unmerged_reflections_iterator;
  typedef scitbx::af::shared<cmil::index<int> > shell;

  struct sorter_by_resolution {
    cuc::unit_cell unit_cell;
    sorter_by_resolution(cuc::unit_cell new_unit_cell):
      unit_cell(new_unit_cell) { }
    bool operator() (cmil::index<int> const & a,
                     cmil::index<int> const & b)
    {
      return unit_cell.d(a) < unit_cell.d(b);
    }
  };

  struct resolutionizer {
    unmerged_reflections ur;
    scitbx::af::shared<cmil::index<int> > s_indices;
    std::vector<shell> shells;
    cuc::unit_cell unit_cell;

    void setup_shells(size_t nshells);
    bool compare_resolution(cmil::index<int> const & a,
                            cmil::index<int> const & b);
    void set_unit_cell(scitbx::af::tiny<double, 6> new_unit_cell);
    void setup(scitbx::af::const_ref<cmil::index<int> > const & indices,
               scitbx::af::const_ref<float> const & i_data,
               scitbx::af::const_ref<float> const & sigi_data);
    float isig(void);
    scitbx::af::shared<float> isig_shells(void);
    scitbx::af::shared<cmil::index<int> > sorted_indices(void);
  };
}
