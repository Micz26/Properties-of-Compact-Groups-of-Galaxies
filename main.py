import pandas as pd
from scipy.stats import shapiro, fligner, f_oneway, ks_2samp, pearsonr
import matplotlib.pyplot as plt
import statistics
from astropy.cosmology import FlatLambdaCDM
from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np

CGS_df = pd.read_csv('C:\\Users\\mikol\\Downloads\\groups.tsv', delimiter='\t')
mean_lsg = CGS_df.groupby('features')['mean_mu'].mean()
print(mean_lsg.iloc[1], mean_lsg.iloc[0])

group1 = CGS_df[CGS_df['features'] == 0]['mean_mu']
group2 = CGS_df[CGS_df['features'] == 1]['mean_mu']
stat1, p1 = shapiro(group1)
stat2, p2 = shapiro(group2)
print(round(p2, 6), round(p1, 6))
stat, p = fligner(group1, group2)
print(round(p, 6))
f_stat, p = f_oneway(group1, group2)
print(round(p, 6))

Galaxies_morphology_df = pd.read_csv('C:\\Users\\mikol\\Downloads\\galaxies_morphology.tsv', delimiter='\t')
Isolated_galaxies_df = pd.read_csv('C:\\Users\\mikol\\Downloads\\isolated_galaxies.tsv', delimiter='\t')

plt.hist([Galaxies_morphology_df['n'], Isolated_galaxies_df['n']], bins=[x for x in range(13)])
plt.show()

Galaxies_morphology_n = Galaxies_morphology_df['n'].values.tolist()
Isolated_galaxies_n = Isolated_galaxies_df['n'].values.tolist()
Galaxies_morphology_n2 = [x for x in Galaxies_morphology_n if x > 2]
Isolated_galaxies_n2 = [x for x in Isolated_galaxies_n if x > 2]
s, p = ks_2samp(Galaxies_morphology_n, Isolated_galaxies_n)
print(len(Galaxies_morphology_n2) / len(Galaxies_morphology_n), len(Isolated_galaxies_n2) / len(Isolated_galaxies_n), p)

Galaxies_morphology_grouped = Galaxies_morphology_df.groupby('Group').agg(
    mean_n=('n', 'mean'),
    mean_T=('T', 'mean')
)
CGS_df_merged = CGS_df.merge(Galaxies_morphology_grouped, on="Group")

CGS_df_merged_n = CGS_df_merged['mean_n'].values.tolist()
CGS_df_merged_T = CGS_df_merged['mean_T'].values.tolist()
CGS_df_merged_mu = CGS_df_merged['mean_mu'].values.tolist()

plt.scatter(CGS_df_merged_n, CGS_df_merged_mu)
plt.scatter(CGS_df_merged_T, CGS_df_merged_mu)
plt.show()

stat3, p3 = shapiro(CGS_df_merged_mu)
stat4, p4 = shapiro(CGS_df_merged_n)
stat5, p5 = shapiro(CGS_df_merged_T)
corr1, p6 = pearsonr(CGS_df_merged_mu, CGS_df_merged_n)
corr2, p7 = pearsonr(CGS_df_merged_mu, CGS_df_merged_T)
print("{:.5f}".format(p3), "{:.5f}".format(p4), "{:.5f}".format(p5), "{:.5f}".format(p6))
print("{:.6f}".format(p7))

cosmo = FlatLambdaCDM(H0=67.74, Om0=0.3089)
z = CGS_df_merged['z'].median()
dA = cosmo.angular_diameter_distance(z).to(u.kpc)
galaxies = pd.read_csv('C:\\Users\\mikol\\Downloads\\galaxies_coordinates.tsv', delimiter="\t")
galaxies = galaxies.dropna()
Group_list = galaxies['Group']
gr = galaxies['Group'].unique()
gr_RA = galaxies['RA']
gr_DEC = galaxies['DEC']
medians = []
group_separations = []
for idx in range(len(Group_list) - 1):
    for idx2 in range(idx + 1, len(Group_list)):
        if Group_list[idx] == Group_list[idx2]:
            p1 = SkyCoord(ra=gr_RA[idx] * u.degree, dec=gr_DEC[idx] * u.degree, frame="fk5")
            p2 = SkyCoord(ra=gr_RA[idx2] * u.degree, dec=gr_DEC[idx2] * u.degree, frame="fk5")
            group_separations.append(p1.separation(p2).value)
        if idx + 1 == idx2 and Group_list[idx] != Group_list[idx2]:
            median = np.median(group_separations) * dA
            medians.append(median.value)
            group_separations = []

plt.scatter(medians, CGS_df_merged['mean_mu'])
plt.show()
CGS_df_merged = CGS_df_merged.dropna()
p8, stat8 = shapiro(medians)
p9, stat9 = shapiro(CGS_df_merged['mean_mu'])
p10, cor10 = pearsonr(medians[:32], CGS_df_merged['mean_mu'])
h2 = medians[1]
print(f"{h2:.4e}", f"{p8:.4e}", f"{p9:.4e}", f"{p10:.4e}")


